from __future__ import annotations

from typing import TYPE_CHECKING

from ...system import Plugin
from . import settings

if TYPE_CHECKING:
    from ...resource import Resource


class ImagePlugin(Plugin):
    """Plugin for Image"""

    # Hooks

    def detect_resource(self, resource: Resource):
        if resource.format in settings.FORMATS:
            resource.datatype = resource.datatype or "image"
            resource.mediatype = resource.mediatype or f"image/{resource.format}"
