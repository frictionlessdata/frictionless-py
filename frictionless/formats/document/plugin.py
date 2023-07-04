from __future__ import annotations

from typing import TYPE_CHECKING

from ...system import Plugin
from . import settings

if TYPE_CHECKING:
    from ...resource import Resource


class DocumentPlugin(Plugin):
    """Plugin for Document"""

    # Hooks

    def detect_resource(self, resource: Resource):
        if resource.format in settings.FORMATS:
            resource.datatype = resource.datatype or "document"
            resource.mediatype = resource.mediatype or f"application/{resource.format}"
