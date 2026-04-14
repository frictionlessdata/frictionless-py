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

    def matches_datatype(self, resource: Resource):
        if resource.format == "json":
            # Short-circuit on resource.datatype to avoid redundant I/O
            # (detect_metadata_type fetches bytes for remote sources)
            return (
                resource.datatype
                or Detector.detect_metadata_type(resource.normpath, format="json")
                or "json"
            )
        if resource.format in ["jsonl", "ndjson"]:
            return "table"
        if resource.format in ["geojson", "topojson"]:
            return "map"

    def detect_resource(self, resource: Resource):
        if resource.format in ["json", "jsonl", "ndjson", "geojson", "topojson"]:
            resource.mediatype = resource.mediatype or f"text/{resource.format}"

    def select_control_class(self, type: Optional[str] = None):
        if type == "json":
            return JsonControl
