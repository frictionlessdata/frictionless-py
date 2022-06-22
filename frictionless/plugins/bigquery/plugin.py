from ...plugin import Plugin
from ... import helpers
from .control import BigqueryControl
from .parser import BigqueryParser
from .storage import BigqueryStorage


# NOTE:
# We need to ensure that the way we detect bigquery service is good enough.
# We don't want to be importing google and checking the type withouth a good reason


class BigqueryPlugin(Plugin):
    """Plugin for BigQuery"""

    code = "bigquery"
    status = "experimental"

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "bigquery":
            return BigqueryControl.from_descriptor(descriptor)

    def create_file(self, file):
        if not file.scheme and not file.format and file.memory:
            if helpers.is_type(file.data, "Resource"):
                file.scheme = ""
                file.format = "bigquery"
                return file

    def create_parser(self, resource):
        if resource.format == "bigquery":
            return BigqueryParser(resource)

    def create_storage(self, name, source, **options):
        if name == "bigquery":
            return BigqueryStorage(source, **options)
