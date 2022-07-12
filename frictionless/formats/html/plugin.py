from ...plugin import Plugin
from .control import HtmlControl
from .parser import HtmlParser


class HtmlPlugin(Plugin):
    """Plugin for HTML"""

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("type") == "html":
            return HtmlControl.from_descriptor(descriptor)

    def create_parser(self, resource):
        if resource.format == "html":
            return HtmlParser(resource)

    def detect_resource(self, resource):
        if resource.format == "html":
            resource.type = "table"
            resource.mediatype = "text/html"
