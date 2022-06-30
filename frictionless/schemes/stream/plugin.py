from ...plugin import Plugin
from .control import StreamControl
from .loader import StreamLoader


class StreamPlugin(Plugin):
    """Plugin for Local Data"""

    code = "stream"

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "stream":
            return StreamControl.from_descriptor(descriptor)

    def create_file(self, file):
        if not file.scheme and not file.format:
            if hasattr(file.data, "read"):
                file.scheme = "stream"
                file.format = ""
                return file

    def create_loader(self, resource):
        if resource.scheme == "stream":
            return StreamLoader(resource)
