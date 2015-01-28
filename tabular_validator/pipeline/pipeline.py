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
from ..utilities import data_table, data_package, csv_dialect, helpers
from .. import exceptions


class ValidationPipeline(object):

    """Validate a (tabular) data source through a validation pipeline.

    Args:
    * validators: A list of validator names to process `data_source`
        * Each name can be a 'shortname' for the default validators
            * e.g., ['structure', 'tableschema']
        * Each name can be a string path to a validator
            * e.g., ['custompackage.CustomValidator', 'schema']
            * Custom validator must implement the Validator API
    * data_package_source: A stream, filepath, string or URL to a Data Package
    * data_source: A buffer, filepath, string or URL to the table data
    * data_format: The format of `data_source`. 'csv' or 'json'
    * csv_dialect_source: A buffer, filepath, string or URL to a CSV dialect spec
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

    def __init__(self, validators=None, data_source=None,
                 data_package_source=None, csv_dialect_source=None,
                 data_format='csv', options=None,
                 workspace=None, dry_run=None):

        self.validators = validators
        self.data_source = data_source
        self.data_format = data_format
        self.options = options or {}
        self.workspace = workspace or tempfile.mkdtemp()
        self.dry_run = dry_run
        self.openfiles = []

        # data package source
        if data_package_source is not None:
            _valid, self.data_package = data_package.validate(
                data_package_source)
            if not _valid:
                raise exceptions.InvalidSpec
            else:
                if not self.dry_run:
                    self.write_file(json.dumps(self.data_package),
                                    'data_package.json')
        else:
            self.data_package = None

        # csv dialect source
        if csv_dialect_source is not None:
            _valid, self.csv_dialect = csv_dialect.validate(
                csv_dialect_source)
            if not _valid:
                raise exceptions.InvalidSpec
            else:
                if not self.dry_run:
                    self.write_file(json.dumps(self.csv_dialect),
                                    'csv_dialect.json')
        else:
            self.csv_dialect = None

        # data source
        self.table = data_table.DataTable(data_source)
        self.openfiles.extend(self.table.openfiles)

        # container for validator reports
        # TODO: Reimplement this as a 'meta' reporter.Report instance
        # i.e.: it should be an interface over yaml or sql backend, not dict
        self.report = {}

        # instantiate all the validators in the pipeline with options.
        self.builtins = helpers.builtin_validators()
        if validators:
            self.pipeline = []
            for v in validators:
                validator_class = self.resolve_validator(v)
                options = self.options.get(validator_class.name, {})
                self.pipeline.append(validator_class(**options))
        else:
            self.pipeline = [self.builtins[v]() for v in
                             helpers.DEFAULT_PIPELINE]

    def write_file(self, data, name):
        """Write a file to the pipeline workspace."""

        filepath = os.path.join(self.workspace, name)
        with io.open(filepath, mode='w+t',encoding='utf-8') as destfile:
            destfile.write(data)

    def resolve_validator(self, validator_name):
        """Return a validator class."""

        if validator_name in self.builtins:
            validator_class = self.builtins[validator_name]
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
        """Run the validation pipeline."""

        # default valid state
        valid = True

        def _run_valid(process_valid, run_valid):
            """Set/maintain the valid state of this run."""
            if not process_valid and run_valid:
                return False
            return run_valid

        # pre_run
        for validator in self.pipeline:
            if hasattr(validator, 'pre_run'):
                _valid, table = validator.pre_run(self.table)
                valid = _run_valid(_valid, valid)
                if not _valid and validator.fail_fast:
                    return valid, self.generate_report()

        # run_header
        for validator in self.pipeline:
            if hasattr(validator, 'run_header'):
                _valid, self.table.headers = validator.run_header(self.table.headers)
                valid = _run_valid(_valid, valid)
                if not _valid and validator.fail_fast:
                    return valid, self.generate_report()

        # run_row
        for validator in self.pipeline:
            if hasattr(validator, 'run_row'):
                # TODO: on transform, create a new stream out of returned rows
                for index, row in enumerate(self.table.values):
                    _valid, index, row = validator.run_row(self.table.headers, index, row)
                    valid = _run_valid(_valid, valid)
                    if not _valid and validator.fail_fast:
                        return valid, self.generate_report()

        # run_column
        # TODO: ensure work is on transformed data (after run_row)
        # for validator in self.pipeline:
        #     if hasattr(validator, 'run_column'):
        #         for index, column in enumerate(self.table.by_column):
        #             _valid, column = validator.run_column(index, column)
        #             valid = _run_valid(_valid, valid)
        #             if not _valid and validator.fail_fast:
        #                 return valid, self.generate_report()

        # post_run
        for validator in self.pipeline:
            if hasattr(validator, 'post_run'):
                _valid, self.table = validator.post_run(self.table)
                valid = _run_valid(_valid, valid)
                if not _valid and validator.fail_fast:
                    return valid, self.generate_report()

        # `dry_run` tasks
        if self.dry_run:
            self.rm_workspace()

        return valid, self.generate_report()

    def rm_workspace(self):
        """Remove this run's workspace from disk."""

        return shutil.rmtree(self.workspace)

    def generate_report(self):
        """Run the report generator for each validator in the pipeline."""

        for validator in self.pipeline:
            self.report[validator.name] = validator.report.generate()

        return self.report
