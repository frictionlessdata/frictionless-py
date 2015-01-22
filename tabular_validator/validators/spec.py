# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import base
from .. import utilities


class SpecValidator(base.Validator):

    """Valid spec files that accompany a tabular data source.

    Args:
        data_package: a valid data pakage spec
        table_schema: a valid JSON Table Schema spec
        csv_dialect: a valid CSV dialect spec

    """

    name = 'spec'
    REMOTE_SCHEMES = ('http', 'https', 'ftp', 'ftps')

    def __init__(self, fail_fast=False, data_package=None, table_schema=None,
                 csv_dialect=None, error_if_none=False):

        super(SpecValidator, self).__init__(fail_fast=fail_fast)

        # TODO: error or warning if spec is missing

        self.table_schema = table_schema
        self.data_package = data_package
        self.csv_dialect = csv_dialect
        self.error_if_none = error_if_none

    def run(self):
        """Override super run method."""
        valid_d = self.validate_data_package()
        valid_t = self.validate_table_schema()
        valid_c = self.validate_csv_dialect()
        return all([valid_d, valid_t, valid_c])

    def validate_data_package(self):
        """Validate that a Data Package file is well formed."""

        if not self.data_package:
            return True

        try:
            self.package_spec = self.load_source(self.data_package)
            if not self.package_spec:
                return False
            else:
                return True

        except ValueError:
             return False

    def validate_table_schema(self):
        """Validate that a JSON Table Schema file is well formed."""

        if not self.table_schema:
            return True

        try:
            self.schema_spec = self.load_source(self.table_schema)
            if not self.schema_spec:
                return False
            else:
                return True

        except ValueError:
            return False

    def validate_csv_dialect(self):
        """Validate that a CSV Dialect file is well formed."""

        if not self.csv_dialect:
            return True

        try:
            self.dialect_spec = self.load_source(self.csv_dialect)
            if not self.dialect_spec:
                return False
            else:
                return True

        except ValueError:
            return False

    def load_source(self, source):
        """Load a spec source into a Python data structure."""
        return utilities.load_json_source(source)
