from ...plugin import Plugin
from .control import StreamControl
from .loader import StreamLoader


class StreamPlugin(Plugin):
    """Plugin for Stream Data"""

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "stream":
            return StreamControl.from_descriptor(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "stream":
            return StreamLoader(resource)

    def detect_resource(self, resource):
        if resource.data is not None:
            if hasattr(resource.data, "read"):
                resource.scheme = "stream"
