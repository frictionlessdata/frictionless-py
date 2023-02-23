from __future__ import annotations
from typing import TYPE_CHECKING
from ...system import Plugin
from .control import HtmlControl
from .parser import HtmlParser

if TYPE_CHECKING:
    from ...resource import Resource


class HtmlPlugin(Plugin):
    """Plugin for HTML"""

    # Hooks

    def create_parser(self, resource):
        if resource.format == "html":
            return HtmlParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.format == "html":
            resource.mediatype = "text/html"

    def select_Control(self, type):
        if type == "html":
            return HtmlControl
