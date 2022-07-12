from ...plugin import Plugin
from .control import JsonControl
from .parsers import JsonParser, JsonlParser


class JsonPlugin(Plugin):
    """Plugin for Json"""

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("type") == "json":
            return JsonControl.from_descriptor(descriptor)

    def create_parser(self, resource):
        if resource.format == "json":
            return JsonParser(resource)
        elif resource.format in ["jsonl", "ndjson"]:
            return JsonlParser(resource)

    def detect_resource(self, resource):
        if resource.format in ["json", "jsonl", "ndjson"]:
            resource.type = "table"
            resource.mediatype = f"text/{resource.format}"
