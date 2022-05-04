from ...plugin import Plugin
from .control import StreamControl
from .loader import StreamLoader


class StreamPlugin(Plugin):
    """Plugin for Local Data

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.stream import StreamPlugin`

    """

    code = "stream"

    def create_file(self, file):
        if not file.scheme and not file.format:
            if hasattr(file.data, "read"):
                file.scheme = "stream"
                file.format = ""
                return file

    def create_control(self, resource, *, descriptor):
        if resource.scheme == "stream":
            return StreamControl(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "stream":
            return StreamLoader(resource)
