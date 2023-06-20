from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ...system import Plugin
from .control import HtmlControl
from .parser import HtmlParser

if TYPE_CHECKING:
    from ...resource import Resource


class HtmlPlugin(Plugin):
    """Plugin for HTML"""

    # Hooks

    def create_parser(self, resource: Resource):
        if resource.format == "html":
            return HtmlParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.format == "html":
            resource.datatype = resource.datatype or "text"
            resource.mediatype = resource.mediatype or "text/html"

    def select_control_class(self, type: Optional[str] = None):
        if type == "html":
            return HtmlControl
