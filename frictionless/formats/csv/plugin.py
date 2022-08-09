from __future__ import annotations
from typing import TYPE_CHECKING
from ...plugin import Plugin
from .control import CsvControl
from .parser import CsvParser

if TYPE_CHECKING:
    from ...interfaces import IDescriptor
    from ...resource import Resource


class CsvPlugin(Plugin):
    """Plugin for CSV"""

    # Hooks

    def create_control(self, descriptor: IDescriptor):  # type: ignore
        if descriptor.get("type") == "csv":
            return CsvControl.from_descriptor(descriptor)  # type: ignore

    def create_parser(self, resource: Resource):
        if resource.format in ["csv", "tsv"]:
            return CsvParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.format in ["csv", "tsv"]:
            resource.type = "table"
            resource.mediatype = f"text/{resource.format}"
