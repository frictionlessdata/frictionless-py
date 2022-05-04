from ...plugin import Plugin
from .dialect import JsonDialect
from .parser import JsonParser, JsonlParser


class JsonPlugin(Plugin):
    """Plugin for Json

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.json import JsonPlugin`

    """

    code = "json"

    def create_dialect(self, resource, *, descriptor):
        if resource.format in ["json", "jsonl", "ndjson"]:
            return JsonDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "json":
            return JsonParser(resource)
        elif resource.format in ["jsonl", "ndjson"]:
            return JsonlParser(resource)
