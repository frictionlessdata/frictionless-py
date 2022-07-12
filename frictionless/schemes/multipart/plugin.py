from ...plugin import Plugin
from .control import MultipartControl
from .loader import MultipartLoader


class MultipartPlugin(Plugin):
    """Plugin for Multipart Data"""

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("type") == "multipart":
            return MultipartControl.from_descriptor(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "multipart":
            return MultipartLoader(resource)

    def detect_resource(self, resource):
        if resource.multipart:
            resource.scheme = "multipart"
