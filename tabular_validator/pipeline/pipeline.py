# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import importlib
import shutil
import tempfile
import json
import csv
from ..utilities import data_table, data_package, csv_dialect, helpers
from .. import exceptions
from .. import compat


class Pipeline(object):

    """Validate a (tabular) data source through a validation pipeline.

    Args:
    * validators: A list of validator names to process `data_source`
        * Each name can be a 'shortname' for the default validators
            * e.g., ['structure', 'tableschema']
        * Each name can be a string path to a validator
            * e.g., ['custompackage.CustomValidator', 'schema']
            * Custom validator must implement the Validator API
    * data: A buffer, filepath, string or URL to the table data
    * format: The format of `data_source`. 'csv' or 'json'
    * dialect: A buffer, filepath, string or URL to a CSV dialect spec
    * options: a dict configuration object for the validation pipeline
        * Each validator has its options nested under its 'shortname'
        * Custom validators have options nested under cls.__name__.lower()
        * e.g.:
            {'structure': {#options}, 'customvalidator': {#options}}
    * workspace: path to directory for files. e.g.: '/my/path'
    * dry_run: No files are persisted after the run has been completed

    Returns:
        A tuple of `valid, report`, where `valid` is a boolean expressing
        validity according to the whole pipeline, and report is a dict
        of the entire pipeline report where each top-level key matches
        a validator in the pipeline.

    """

    ROW_LIMIT_MAX = 30000
    REPORT_LIMIT_MAX = 1000
    SOURCE_FILENAME = 'source.csv'
    TRANSFORM_FILENAME = 'transform.csv'
    DIALECT_FILENAME = 'dialect.json'

    def __init__(self, data, validators=None, dialect=None, format='csv',
                 options=None, workspace=None, dry_run=True, transform=True,
                 row_limit=20000, report_limit=1000, report_stream=None):

        if data is None:
            _msg = '`data` must be a filepath, url or stream.'
            raise exceptions.PipelineBuildError(_msg)

        if report_stream:
            report_stream_tests = [isinstance(report_stream, io.TextIOBase),
                                   report_stream.writable(),
                                   report_stream.seekable()]

            if not all(report_stream_tests):
                _msg = '`report_stream` must be a seekable and writable text stream.'
                raise exceptions.PipelineBuildError(_msg)

        self.openfiles = []
        self.validators = validators or helpers.DEFAULT_PIPELINE
        self.dialect = self.get_dialect(dialect)
        self.format = format
        self.options = options or {}
        self.dry_run = dry_run
        self.workspace = self.get_workspace(workspace)
        self.transform = transform
        self.row_limit = self.get_row_limit(row_limit)
        self.report_limit = self.get_report_limit(report_limit)
        self.report_stream = report_stream
        self.pipeline = self.get_pipeline()
        self.data = data_table.DataTable(data)
        self.report = {}
        self.openfiles.extend(self.data.openfiles)

        if not self.dry_run:
            self.init_workspace()

    def init_workspace(self):
        """Initalize the workspace for this run."""

        self.create_file(self.data.stream, self.SOURCE_FILENAME, self.data.headers)
        self.create_file('', self.TRANSFORM_FILENAME)
        self.create_file(json.dumps(self.dialect), self.DIALECT_FILENAME)

    def get_workspace(self, filepath):
        """Return a workspace for this run."""
        # TODO: use pudo/barn

        if not self.dry_run:
            return filepath or tempfile.mkdtemp()

        return None

    def get_pipeline(self):
        """Get the pipeline for this instance."""

        pipeline = []
        for name in self.validators:
            _class = self.resolve_validator(name)
            options = self.options.get(_class.name, {})
            # override options with those we accept directly from the pipeline
            options['row_limit'] = self.row_limit
            options['report_limit'] = self.report_limit
            options['report_stream'] = self.report_stream
            options['transform'] = self.transform
            pipeline.append(_class(**options))

        return pipeline

    def get_dialect(self, dialect_source):
        """Get a CSV dialect instance for this data."""

        if dialect_source:
            _valid, rv = csv_dialect.validate(dialect_source)
            if not _valid:
                raise exceptions.InvalidSpec
            return rv
        else:
            return None

    def get_row_limit(self, passed_limit):
        """Return the row limit, locked to an upper limit."""

        if passed_limit > self.ROW_LIMIT_MAX:
            return self.ROW_LIMIT_MAX
        else:
            return passed_limit

    def get_report_limit(self, passed_limit):
        """Return the report_limit, locked to an upper limit."""

        if passed_limit > self.REPORT_LIMIT_MAX:
            return self.REPORT_LIMIT_MAX
        else:
            return passed_limit

    def create_file(self, data, name, headers=None):
        """Create a file in the pipeline workspace."""

        filepath = os.path.join(self.workspace, name)
        with io.open(filepath, mode='w+t', encoding='utf-8') as destfile:
            if headers:
                destfile.write(','.join(headers))

            if isinstance(data, compat.str):
                destfile.write(data)
            elif isinstance(data, compat.bytes):
                # TODO: We should not ever deal with bytes here: see why we are (or if we still are)
                destfile.write(data.decode('utf-8'))
            else:
                destfile.write(data.read())
                data.seek(0)

    def resolve_validator(self, validator_name):
        """Return a validator class."""

        if validator_name in helpers.builtin_validators():
            validator_class = helpers.builtin_validators()[validator_name]
        else:
            # resolve a custom validator
            _module, _class = validator_name.rsplit('.', 1)
            try:
                validator_class = getattr(importlib.import_module(_module),
                                          _class)
            except ImportError as e:
                # TODO: something better here
                raise e

        return validator_class

    def register_validator(self, validator_name, options=None, position=None):
        """Register a validator on the pipeline."""

        validator_class = self.resolve_validator(validator_name)
        options = options or {}
        validator = validator_class(**options)

        if position is None:
            self.pipeline.append(validator)
        else:
            self.pipeline.insert(position, validator)

    def run(self):
        """Run the pipeline."""

        valid = True

        for validator in self.pipeline:

            valid, self.report[validator.name], self.data = \
                validator.run(self.data, is_table=True)

            # if a validator returns invalid, we stop the pipeline
            if not valid:
                return valid, self.generate_report()

            if not self.dry_run and self.transform:
                # TODO: do what we'll do with transform data, workspace, etc.
                pass
            else:
                self.data.replay()

        return valid, self.generate_report()

    def rm_workspace(self):
        """Remove this run's workspace from disk."""

        return shutil.rmtree(self.workspace)

    def generate_report(self):
        """Run the report generator for each validator in the pipeline."""

        generated = dict(self.report)
        for k, v in generated.items():
            generated[k] = v.generate()

        return generated
