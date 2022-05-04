from ...plugin import Plugin
from .dialect import CsvDialect
from .parser import CsvParser


class CsvPlugin(Plugin):
    """Plugin for Pandas

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.csv import CsvPlugin`

    """

    code = "csv"

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "csv":
            return CsvDialect(descriptor)
        elif resource.format == "tsv":
            return CsvDialect(descriptor, delimiter="\t")

    def create_parser(self, resource):
        if resource.format in ["csv", "tsv"]:
            return CsvParser(resource)
