from __future__ import annotations
from typing import TYPE_CHECKING
from ...system import Plugin
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

    def detect_path_resource(self, resource: Resource):
        if resource.format in ["json", "jsonl", "ndjson"]:
            resource.mediatype = f"text/{resource.format}"

    def detect_resource_type(self, resource: Resource):
        if resource.format in ["jsonl", "ndjson"]:
            return "table"

    def select_Control(self, type):
        if type == "json":
            return JsonControl
