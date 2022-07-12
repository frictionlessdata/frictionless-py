from ...plugin import Plugin
from .control import CsvControl
from .parser import CsvParser


class CsvPlugin(Plugin):
    """Plugin for CSV"""

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("type") == "csv":
            return CsvControl.from_descriptor(descriptor)

    def create_parser(self, resource):
        if resource.format in ["csv", "tsv"]:
            return CsvParser(resource)

    def detect_resource(self, resource):
        if resource.format in ["csv", "tsv"]:
            resource.type = "table"
            resource.mediatype = f"text/{resource.format}"
