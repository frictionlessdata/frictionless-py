from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ...system import Plugin
from .control import GsheetsControl
from .parser import GsheetsParser

if TYPE_CHECKING:
    from ...resource import Resource


class GsheetsPlugin(Plugin):
    """Plugin for Google Sheets"""

    # Hooks

    def create_parser(self, resource: Resource):
        if resource.format == "gsheets":
            return GsheetsParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.path:
            if "docs.google.com/spreadsheets" in resource.path:
                resource.datatype = resource.datatype or "table"
                if "export" not in resource.path and "pub" not in resource.path:
                    resource.format = resource.format or "gsheets"
                elif "csv" in resource.path:
                    resource.scheme = resource.scheme or "https"
                    resource.format = resource.format or "csv"
                    resource.mediatype = resource.mediatype or "text/csv"

    def select_control_class(self, type: Optional[str] = None):
        if type == "gsheets":
            return GsheetsControl
