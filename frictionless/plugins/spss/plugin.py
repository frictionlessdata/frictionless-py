from ...plugin import Plugin
from .dialect import SpssDialect
from .parser import SpssParser


class SpssPlugin(Plugin):
    """Plugin for SPSS

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.spss import SpssPlugin`
    """

    code = "spss"
    status = "experimental"

    def create_dialect(self, resource, *, descriptor):
        if resource.format in ["sav", "zsav"]:
            return SpssDialect(descriptor)

    def create_parser(self, resource):
        if resource.format in ["sav", "zsav"]:
            return SpssParser(resource)
