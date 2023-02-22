from __future__ import annotations
from ...system import Plugin
from ...records import PathDetails
from .control import GsheetsControl
from .parser import GsheetsParser


class GsheetsPlugin(Plugin):
    """Plugin for Google Sheets"""

    # Hooks

    def create_parser(self, resource):
        if resource.format == "gsheets":
            return GsheetsParser(resource)

    def detect_path_details(self, details: PathDetails):
        if details.path:
            if "docs.google.com/spreadsheets" in details.path:
                details.type = "table"
                if "export" not in details.path and "pub" not in details.path:
                    details.scheme = ""
                    details.format = "gsheets"
                elif "csv" in details.path:
                    details.scheme = "https"
                    details.format = "csv"

    def select_Control(self, type):
        if type == "gsheets":
            return GsheetsControl
