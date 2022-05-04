from ...plugin import Plugin
from .control import S3Control
from .loader import S3Loader


class S3Plugin(Plugin):
    """Plugin for S3

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.s3 import S3Plugin`

    """

    code = "s3"
    status = "experimental"

    def create_control(self, resource, *, descriptor):
        if resource.scheme == "s3":
            return S3Control(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "s3":
            return S3Loader(resource)
