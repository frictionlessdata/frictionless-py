from ...plugin import Plugin
from .control import MultipartControl
from .loader import MultipartLoader


class MultipartPlugin(Plugin):
    """Plugin for Multipart Data"""

    code = "multipart"
    status = "experimental"

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "multipart":
            return MultipartControl.from_descriptor(descriptor)

    def create_file(self, file):
        if file.multipart:
            file.scheme = "multipart"
            return file

    def create_loader(self, resource):
        if resource.scheme == "multipart":
            return MultipartLoader(resource)
