from ...plugin import Plugin
from .control import HtmlControl
from .parser import HtmlParser


class HtmlPlugin(Plugin):
    """Plugin for HTML"""

    code = "html"
    status = "experimental"

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "html":
            return HtmlControl.from_descriptor(descriptor)

    def create_parser(self, resource):
        if resource.format == "html":
            return HtmlParser(resource)
