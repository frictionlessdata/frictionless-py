from ...plugin import Plugin
from .control import AwsControl
from .loaders import S3Loader


class AwsPlugin(Plugin):
    """Plugin for Aws"""

    code = "aws"

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "s3":
            return AwsControl.from_descriptor(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "s3":
            return S3Loader(resource)
