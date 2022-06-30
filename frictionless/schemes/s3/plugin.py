from ...plugin import Plugin
from .control import S3Control
from .loader import S3Loader


class S3Plugin(Plugin):
    """Plugin for S3"""

    code = "s3"

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "s3":
            return S3Control.from_descriptor(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "s3":
            return S3Loader(resource)
