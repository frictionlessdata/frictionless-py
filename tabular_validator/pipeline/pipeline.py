# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import importlib
from ..validators import SpecValidator
from .. import utilities
from .. import exceptions


class ValidationPipeline(object):

    """Validate a (tabular) data source through a validation pipeline.

    Args:
        validators: A list of validator names to process `data_source`
            * Each name can be a 'shortname' for the default validators
                * e.g., ['structure', 'schema', 'probe']
            * Each name can be a string path to a validator
                * e.g., ['custompackage.CustomValidator', 'schema']
                * Custom validator must implement the Validator API
        data_package: A stream, filepath, string or URL for a Data Package spec
        data_source: A buffer, filepath, string or URL to the table data
        data_format: The format of `data_source`. 'csv' or 'json'
        table_schema: A buffer, filepath, string or URL for a JSON Table Schema
        csv_dialect: A buffer, filepath, string or URL for a CSV dialect spec

        options: a dict configuration object for the validation pipeline
            * Each validator has its options nested under its 'shortname'
            * Custom validators have options nested under a lower case string
                of the Class name
            * e.g.:
                {'structure': {#options}, 'customvalidator': {#options}}

    Returns:
        A tuple of `valid, report`, where `valid` is a boolean expressing
        validity according to the whole pipeline, and report is a dict
        of the entire pipeline report where each top-level key matches
        a validator in the pipeline.

    """

    def __init__(self, validators=None, data_package=None, data_source=None,
                 data_format='csv', table_schema=None, csv_dialect=None,
                 options=None, job_id=None, workspace=None, dry_run=None):

        # TODO: Handle data_format (CSV, JSON)
        # TODO: Pass csv_dialect to the table constructor
        # TODO: Handle data_package and everything that means
        # TODO: Handle cases where validators arguments are not valid
        # TODO: Ensure that options looks legit

        # TODO: Support job_id
        # TODO: Support workspace
        # TODO: Support dry_run

        self.validators = validators
        self.data_package = data_package
        self.data_source = data_source
        self.data_format = data_format
        self.table_schema = table_schema
        self.csv_dialect = csv_dialect
        self.options = options or {}
        self.openfiles = []

        # Check that any/all spec files are validly formed
        valid = self.validate_spec()
        if not valid:
            raise exceptions.InvalidSpec

        self.table = utilities.DataTable(data_source)
        self.openfiles.extend(self.table.openfiles)
        self.report = {}

        self.builtins = utilities.builtin_validators()

        # instantiate all the validators in the pipeline with options.
        if validators:
            self.pipeline = []
            for v in validators:
                validator_class = self.resolve_validator(v)
                options = self.options.get(validator_class.name, {})
                self.pipeline.append(validator_class(**options))
        else:
            self.pipeline = [self.builtins[v]() for v in
                             utilities.DEFAULT_PIPELINE]

    def validate_spec(self):
        """Validate any/all spec files."""
        specs = [self.data_package, self.table_schema, self.csv_dialect]
        if any(specs):
            sv = SpecValidator(data_package=self.data_package,
                               table_schema=self.table_schema,
                               csv_dialect=self.csv_dialect)
            return sv.run()

        return True

    def resolve_validator(self, validator_name):
        """Return a validator class."""

        if validator_name in self.builtins:
            validator_class = self.builtins[validator_name]

        else:
            # a custom validator
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

        # The valid state of the run
        valid = True

        def _run_valid(process_valid, run_valid):
            """Set/maintain the valid state of the run."""
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

        return valid, self.generate_report()

    def generate_report(self):
        """Run the report generator for each validator in the pipeline."""

        for validator in self.pipeline:
            self.report[validator.name] = validator.report.generate()

        return self.report
