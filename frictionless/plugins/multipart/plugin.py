from ...plugin import Plugin
from .control import MultipartControl
from .loader import MultipartLoader


class MultipartPlugin(Plugin):
    """Plugin for Multipart Data

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.multipart import MultipartPlugin`

    """

    code = "multipart"
    status = "experimental"

    def create_file(self, file):
        if file.multipart:
            file.scheme = "multipart"
            return file

    def create_control(self, resource, *, descriptor):
        if resource.scheme == "multipart":
            return MultipartControl(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "multipart":
            return MultipartLoader(resource)
