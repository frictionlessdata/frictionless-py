from ...plugin import Plugin
from .control import ExcelControl
from .parsers import XlsxParser, XlsParser


class ExcelPlugin(Plugin):
    """Plugin for Excel"""

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "excel":
            return ExcelControl.from_descriptor(descriptor)

    def create_parser(self, resource):
        if resource.format == "xlsx":
            return XlsxParser(resource)
        elif resource.format == "xls":
            return XlsParser(resource)

    def detect_resource(self, resource):
        if resource.format in ["xlsx", "xls"]:
            resource.type = "table"
            resource.mediatype = "application/vnd.ms-excel"
