from __future__ import annotations
from ...plugin import Plugin
from .control import BufferControl
from .loader import BufferLoader


class BufferPlugin(Plugin):
    """Plugin for Buffer Data"""

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("type") == "buffer":
            return BufferControl.from_descriptor(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "buffer":
            return BufferLoader(resource)

    def detect_resource(self, resource):
        if resource.data is not None:
            if isinstance(resource.data, bytes):
                resource.scheme = "buffer"
        elif resource.scheme == "buffer":
            resource.data = b""
