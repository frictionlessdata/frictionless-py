from ...plugin import Plugin
from .dialect import GsheetsDialect
from .parser import GsheetsParser


class GsheetsPlugin(Plugin):
    """Plugin for Google Sheets

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.gsheets import GsheetsPlugin`

    """

    code = "gsheet"
    status = "experimental"

    def create_file(self, file):
        if not file.memory:
            if "docs.google.com/spreadsheets" in file.path:
                if "export" not in file.path and "pub" not in file.path:
                    file.scheme = ""
                    file.format = "gsheets"
                elif "csv" in file.path:
                    file.scheme = "https"
                    file.format = "csv"
                return file

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "gsheets":
            return GsheetsDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "gsheets":
            return GsheetsParser(resource)
