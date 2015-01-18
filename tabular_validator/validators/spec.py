import io
import json
import codecs
from urllib import request, parse
# from jsonschema import Draft4Validator, SchemaError
from . import base


class SpecValidator(base.Validator):

    """Valid spec files that accompany a tabular data source.

    Args:
        data_package: a valid data pakage spec
        table_schema: a valid JSON Schema spec (e.g.: JSON Table Schema spec)
        csv_dialect: a valid CSV dialect source

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
        """Validate that a Data Package descriptor is well formed."""
        try:
            self.package_spec = self.load_source(self.data_package)
            return True
        except ValueError:
            # TODO: set on report
            return False
            # TODO: check it is actually as expected

    def validate_table_schema(self):
        """Validate that a JSON Table Schema descriptor is well formed."""
        try:
            self.schema_spec = self.load_source(self.table_schema)
            if not self.schema_spec:
                return False
            else:
                return True
        except ValueError:
            # TODO: set on report
            return False

        # try:
        #     valid = Draft4Validator.check_schema(self.schema_spec)
        #     return valid
        # except SchemaError:
        #     # TODO: set on report
        #     return False

    def validate_csv_dialect(self):
        """Validate that a CSV Dialect descriptor is well formed."""
        try:
            self.dialect_spec = self.load_source(self.csv_dialect)
            return True
        except ValueError:
            # TODO: set on report
            return False
        # TODO: Check it is actually as expected

    def load_source(self, source):
        """Load a spec source into a Python data structure."""

        if isinstance(source, (dict, list)):
            # The source has already been loaded
            return source

        if source is None:
            return None

        elif parse.urlparse(source).scheme in self.REMOTE_SCHEMES:
            payload = codecs.decode(
                request.urlopen(source).read(), 'utf-8')
            return json.loads(payload)

        else:
            with io.open(source) as stream:
                source = json.load(stream)
            return source
