from __future__ import annotations
from typing import TYPE_CHECKING
from ...system import Plugin
from .control import BufferControl
from .loader import BufferLoader

if TYPE_CHECKING:
    from ...resource import Resource


class BufferPlugin(Plugin):
    """Plugin for Buffer Data"""

    # Hooks

    def create_loader(self, resource):
        if resource.scheme == "buffer":
            return BufferLoader(resource)

    def detect_resource(self, resource: Resource):
        if resource.data is not None:
            if isinstance(resource.data, bytes):
                resource.scheme = "buffer"
        elif resource.scheme == "buffer":
            resource.data = b""

    def select_control_class(self, type):
        if type == "buffer":
            return BufferControl
