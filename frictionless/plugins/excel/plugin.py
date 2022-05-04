from ...plugin import Plugin
from .dialect import ExcelDialect
from .parser import XlsxParser, XlsParser


class ExcelPlugin(Plugin):
    """Plugin for Excel

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.excel import ExcelPlugin`

    """

    code = "excel"

    def create_dialect(self, resource, *, descriptor):
        if resource.format in ["xlsx", "xls"]:
            return ExcelDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "xlsx":
            return XlsxParser(resource)
        elif resource.format == "xls":
            return XlsParser(resource)
