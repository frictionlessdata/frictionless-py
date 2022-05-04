from ...plugin import Plugin
from ... import helpers
from .dialect import BigqueryDialect
from .parser import BigqueryParser
from .storage import BigqueryStorage


# NOTE:
# We need to ensure that the way we detect bigquery service is good enough.
# We don't want to be importing google and checking the type withouth a good reason


class BigqueryPlugin(Plugin):
    """Plugin for BigQuery

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.bigquery import BigqueryPlugin`
    """

    code = "bigquery"
    status = "experimental"

    def create_file(self, file):
        if not file.scheme and not file.format and file.memory:
            if helpers.is_type(file.data, "Resource"):
                file.scheme = ""
                file.format = "bigquery"
                return file

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "bigquery":
            return BigqueryDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "bigquery":
            return BigqueryParser(resource)

    def create_storage(self, name, source, **options):
        if name == "bigquery":
            return BigqueryStorage(source, **options)
