from __future__ import annotations
from ...records import PathDetails
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

    def detect_path_details(self, details: PathDetails):
        if details.format in ["json", "jsonl", "ndjson"]:
            details.mediatype = f"text/{details.format}"
            if details.format in ["jsonl", "ndjson"]:
                details.type = "table"

    def select_Control(self, type):
        if type == "json":
            return JsonControl
