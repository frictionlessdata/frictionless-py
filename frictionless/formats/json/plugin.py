from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ...detector import Detector
from ...system import Plugin
from .control import JsonControl
from .parsers import JsonlParser, JsonParser

if TYPE_CHECKING:
    from ...resource import Resource


class JsonPlugin(Plugin):
    """Plugin for Json"""

    # Hooks

    def create_parser(self, resource: Resource):
        if resource.format == "json":
            return JsonParser(resource)
        elif resource.format in ["jsonl", "ndjson"]:
            return JsonlParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.format in ["json", "jsonl", "ndjson", "geojson", "topojson"]:
            resource.mediatype = resource.mediatype or f"text/{resource.format}"
            if resource.format == "json":
                resource.datatype = (
                    resource.datatype
                    or Detector.detect_metadata_type(resource.normpath, format="json")
                    or "json"
                )
            if resource.format in ["jsonl", "ndjson"]:
                resource.datatype = resource.datatype or "table"
            if resource.format in ["geojson", "topojson"]:
                resource.datatype = resource.datatype or "map"

    def select_control_class(self, type: Optional[str] = None):
        if type == "json":
            return JsonControl
