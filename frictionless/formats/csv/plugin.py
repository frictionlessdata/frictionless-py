from __future__ import annotations
from typing import TYPE_CHECKING
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
            resource.type = "table"
            resource.mediatype = f"text/{resource.format}"

    def select_Control(self, type: str):
        if type == "csv":
            return CsvControl
