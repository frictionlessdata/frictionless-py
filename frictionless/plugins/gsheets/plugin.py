from ...plugin import Plugin
from .control import GsheetsControl
from .parser import GsheetsParser


class GsheetsPlugin(Plugin):
    """Plugin for Google Sheets"""

    code = "gsheet"
    status = "experimental"

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "gsheets":
            return GsheetsControl.from_descriptor(descriptor)

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

    def create_parser(self, resource):
        if resource.format == "gsheets":
            return GsheetsParser(resource)
