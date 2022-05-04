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

    def create_file(self, file):
        if not file.scheme and not file.format:
            if isinstance(file.data, bytes):
                file.scheme = "buffer"
                file.format = ""
                return file

    def create_control(self, resource, *, descriptor):
        if resource.scheme == "buffer":
            return BufferControl(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "buffer":
            return BufferLoader(resource)
