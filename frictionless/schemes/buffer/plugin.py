from ...plugin import Plugin
from .control import BufferControl
from .loader import BufferLoader


class BufferPlugin(Plugin):
    """Plugin for Buffer Data"""

    code = "buffer"

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "buffer":
            return BufferControl.from_descriptor(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "buffer":
            return BufferLoader(resource)

    def create_resource(self, resource):
        if resource.data:
            if isinstance(resource.data, bytes):
                resource.scheme = "buffer"
