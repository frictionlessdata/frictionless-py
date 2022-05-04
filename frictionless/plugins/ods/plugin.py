from ...plugin import Plugin
from .dialect import OdsDialect
from .parser import OdsParser


class OdsPlugin(Plugin):
    """Plugin for ODS

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.ods import OdsPlugin`

    """

    code = "ods"

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "ods":
            return OdsDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "ods":
            return OdsParser(resource)
