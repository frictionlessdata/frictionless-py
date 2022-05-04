from ...plugin import Plugin
from .dialect import HtmlDialect
from .parser import HtmlParser


class HtmlPlugin(Plugin):
    """Plugin for HTML

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.html import HtmlPlugin`

    """

    code = "html"
    status = "experimental"

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "html":
            return HtmlDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "html":
            return HtmlParser(resource)
