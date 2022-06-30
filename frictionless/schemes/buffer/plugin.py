from ...plugin import Plugin
from .control import BufferControl
from .loader import BufferLoader


class BufferPlugin(Plugin):
    """Plugin for Buffer Data

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.local import BufferPlugin`

    """

    code = "buffer"

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "buffer":
            return BufferControl.from_descriptor(descriptor)

    def create_file(self, file):
        if not file.scheme and not file.format:
            if isinstance(file.data, bytes):
                file.scheme = "buffer"
                file.format = ""
                return file

    def create_loader(self, resource):
        if resource.scheme == "buffer":
            return BufferLoader(resource)
