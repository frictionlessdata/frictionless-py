from ...plugin import Plugin
from .control import GsheetsControl
from .parser import GsheetsParser


class GsheetsPlugin(Plugin):
    """Plugin for Google Sheets"""

    code = "gsheet"

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "gsheets":
            return GsheetsControl.from_descriptor(descriptor)

    def create_parser(self, resource):
        if resource.format == "gsheets":
            return GsheetsParser(resource)

    def detect_resource(self, resource):
        if resource.path:
            if "docs.google.com/spreadsheets" in resource.path:
                resource.type = "table"
                if "export" not in resource.path and "pub" not in resource.path:
                    resource.scheme = ""
                    resource.format = "gsheets"
                elif "csv" in resource.path:
                    resource.scheme = "https"
                    resource.format = "csv"
