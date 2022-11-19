from __future__ import annotations
from ...system import Plugin
from .control import HtmlControl
from .parser import HtmlParser


class HtmlPlugin(Plugin):
    """Plugin for HTML"""

    # Hooks

    def create_parser(self, resource):
        if resource.format == "html":
            return HtmlParser(resource)

    def detect_resource(self, resource):
        if resource.format == "html":
            resource.mediatype = "text/html"

    def select_Control(self, type):
        if type == "html":
            return HtmlControl
