from __future__ import annotations
from ...system import Plugin
from .control import GsheetsControl
from .parser import GsheetsParser


class GsheetsPlugin(Plugin):
    """Plugin for Google Sheets"""

    # Hooks

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

    def select_Control(self, type):
        if type == "gsheets":
            return GsheetsControl
