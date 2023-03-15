from __future__ import annotations
from typing import TYPE_CHECKING
from ...system import Plugin
from ...detector import Detector
from .control import JsonControl
from .parsers import JsonParser, JsonlParser

if TYPE_CHECKING:
    from ...resource import Resource


class JsonPlugin(Plugin):
    """Plugin for Json"""

    # Hooks

    def create_parser(self, resource):
        if resource.format == "json":
            return JsonParser(resource)
        elif resource.format in ["jsonl", "ndjson"]:
            return JsonlParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.format in ["json", "jsonl", "ndjson"]:
            resource.mediatype = resource.mediatype or f"text/{resource.format}"
            if resource.format == "json":
                resource.datatype = (
                    resource.datatype
                    or Detector.detect_metadata_type(resource.normpath, format="json")
                    or "json"
                )
            if resource.format in ["jsonl", "ndjson"]:
                resource.datatype = resource.datatype or "table"

    def select_control_class(self, type):
        if type == "json":
            return JsonControl
