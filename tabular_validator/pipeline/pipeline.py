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

    def __init__(self, validators=None, data=None, dialect=None, format='csv',
                 options=None, workspace=None, dry_run=True):

        self.validators = validators
        self.data = data
        self.format = format
        self.options = options or {}
        self.workspace = workspace or tempfile.mkdtemp()
        self.dry_run = dry_run
        self.openfiles = []

        # csv dialect source
        if dialect:
            _valid, self.dialect = csv_dialect.validate(dialect)
            if not _valid:
                raise exceptions.InvalidSpec
            else:
                if not self.dry_run:
                    self.create_file(json.dumps(self.dialect),
                                     'dialect.json')
        else:
            self.dialect = None

        # original data source
        if not self.dry_run:
            self.create_file('', 'data.csv')
        self.table = data_table.DataTable(data)

        # transformed data_source
        if not self.dry_run:
            self.create_file('', 'transform.csv')
        self.transform = None # Becomes a DataTable if transform occurs

        # files we need to close later
        self.openfiles.extend(self.table.openfiles)

        # container for validator reports
        # TODO: Reimplement this as a 'meta' reporter.Report instance
        # i.e.: it should be an interface over yaml or sql backend, not dict
        self.report = {}

        # instantiate all the validators in the pipeline with options.
        self.builtins = helpers.builtin_validators()
        if self.validators:
            self.pipeline = []
            for v in self.validators:
                validator_class = self.resolve_validator(v)
                options = self.options.get(validator_class.name, {})
                self.pipeline.append(validator_class(**options))
        else:
            self.pipeline = [self.builtins[v]() for v in
                             helpers.DEFAULT_PIPELINE]

    def create_file(self, data, name):
        """Create a file in the pipeline workspace."""

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
        headers, values = self.table.headers, self.table.values

        def _run_valid(process_valid, run_valid):
            """Set/maintain the valid state of this run."""
            if not process_valid and run_valid:
                return False
            return run_valid

        for validator in self.pipeline:

            # replay the table
            headers, values = self.table.replay()

            if validator.transform and not self.dry_run:
                if self.transform:
                    self.transform.stream.seek(0)
                    headers, values = self.transform.headers, self.transform.values
                _t = os.path.join(self.workspace, 'transformed.csv')
                # transform stream
                # raw = io.BufferedRandom(io.BytesIO())
                # stream = io.TextIOWrapper(raw)
                transform = io.open(_t, mode='w+t', encoding='utf-8')
                csvtransform = csv.writer(transform)

            # pre_run
            if hasattr(validator, 'pre_run'):
                _valid, headers, values = validator.pre_run(headers, values)
                valid = _run_valid(_valid, valid)
                if not _valid and validator.fail_fast:
                    return valid, self.generate_report()

            # run_header
            if hasattr(validator, 'run_header'):
                _valid, headers = validator.run_header(headers)
                valid = _run_valid(_valid, valid)
                if not _valid and validator.fail_fast:
                    return valid, self.generate_report()

            # run_row
            if hasattr(validator, 'run_row'):
                for index, row in enumerate(values):
                    old_row = row
                    _valid, headers, index, row = validator.run_row(headers, index, row)
                    valid = _run_valid(_valid, valid)
                    if not _valid and validator.fail_fast:
                        return valid, self.generate_report()

                    if validator.transform and not self.dry_run and row is not None:
                        csvtransform.writerow(row)

            # run_column
            # if hasattr(validator, 'run_column'):
            #     for index, column in enumerate(self.table.by_column):
            #         _valid, column = validator.run_column(index, column)
            #         valid = _run_valid(_valid, valid)
            #         if not _valid and validator.fail_fast:
            #             return valid, self.generate_report()

            # post_run
            if hasattr(validator, 'post_run'):
                _valid, headers, values = validator.post_run(headers, values)
                valid = _run_valid(_valid, valid)
                if not _valid and validator.fail_fast:
                    return valid, self.generate_report()

            if validator.transform and not self.dry_run:
                self.transform = data_table.DataTable(transform, headers=headers)

        return valid, self.generate_report()

    def rm_workspace(self):
        """Remove this run's workspace from disk."""
        return shutil.rmtree(self.workspace)

    def generate_report(self):
        """Run the report generator for each validator in the pipeline."""

        for validator in self.pipeline:
            self.report[validator.name] = validator.report.generate()

        return self.report
