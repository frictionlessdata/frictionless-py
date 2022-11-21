from __future__ import annotations
from ...system import Plugin
from .control import JsonControl
from .parsers import JsonParser, JsonlParser


class JsonPlugin(Plugin):
    """Plugin for Json"""

    # Hooks

    def create_parser(self, resource):
        if resource.format == "json":
            return JsonParser(resource)
        elif resource.format in ["jsonl", "ndjson"]:
            return JsonlParser(resource)

    def detect_resource(self, resource):
        if resource.format in ["json", "jsonl", "ndjson"]:
            resource.mediatype = f"text/{resource.format}"
            if resource.format in ["jsonl", "ndjson"]:
                resource.type = "table"

    def select_Control(self, type):
        if type == "json":
            return JsonControl
