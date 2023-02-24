from __future__ import annotations
from typing import TYPE_CHECKING
from ...system import Plugin

if TYPE_CHECKING:
    from ...resource import Resource


class MarkdownPlugin(Plugin):
    """Plugin for Markdown"""

    # Hooks

    def detect_resource(self, resource: Resource):
        if resource.format == "md":
            resource.mediatype = "text/markdown"

    def detect_resource_type(self, resource: Resource):
        if resource.format == "md":
            return "text"
