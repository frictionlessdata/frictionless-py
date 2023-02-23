from __future__ import annotations
from typing import TYPE_CHECKING
from ...system import Plugin
from .control import GsheetsControl
from .parser import GsheetsParser

if TYPE_CHECKING:
    from ...resource import Resource


class GsheetsPlugin(Plugin):
    """Plugin for Google Sheets"""

    # Hooks

    def create_parser(self, resource):
        if resource.format == "gsheets":
            return GsheetsParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.path:
            if "docs.google.com/spreadsheets" in resource.path:
                if "export" not in resource.path and "pub" not in resource.path:
                    resource.format = "gsheets"
                elif "csv" in resource.path:
                    resource.scheme = "https"
                    resource.format = "csv"

    def detect_resource_type(self, resource: Resource):
        if resource.format == "gsheets":
            return "table"

    def select_Control(self, type):
        if type == "gsheets":
            return GsheetsControl
