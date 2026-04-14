from __future__ import annotations

from typing import TYPE_CHECKING

from ...system import Plugin
from . import settings

if TYPE_CHECKING:
    from ...resource import Resource


class ImagePlugin(Plugin):
    """Plugin for Image"""

    # Hooks

    def matches_datatype(self, resource: Resource):
        if resource.format in settings.FORMATS:
            return "image"

    def detect_resource(self, resource: Resource):
        if resource.format in settings.FORMATS:
            resource.mediatype = resource.mediatype or f"image/{resource.format}"
