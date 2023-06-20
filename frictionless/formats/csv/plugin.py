from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ...system import Plugin
from .control import CsvControl
from .parser import CsvParser

if TYPE_CHECKING:
    from ...resource import Resource


class CsvPlugin(Plugin):
    """Plugin for CSV"""

    # Hooks

    def create_parser(self, resource: Resource):
        if resource.format in ["csv", "tsv"]:
            return CsvParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.format in ["csv", "tsv"]:
            resource.datatype = resource.datatype or "table"
            resource.mediatype = resource.mediatype or f"text/{resource.format}"

    def select_control_class(self, type: Optional[str] = None):
        if type == "csv":
            return CsvControl
