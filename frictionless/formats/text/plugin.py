from __future__ import annotations

from typing import TYPE_CHECKING

from ...system import Plugin
from . import settings

if TYPE_CHECKING:
    from ...resource import Resource


class TextPlugin(Plugin):
    """Plugin for Text"""

    # Hooks

    def detect_resource(self, resource: Resource):
        if resource.name in settings.NAMES or resource.format in settings.FORMATS:
            format = resource.format or "txt"
            resource.datatype = resource.datatype or "text"
            resource.mediatype = resource.mediatype or f"text/{format}"
