from __future__ import annotations
from ...system import Plugin
from .control import AwsControl
from .loaders import S3Loader


class AwsPlugin(Plugin):
    """Plugin for Aws"""

    # Hooks

    def create_loader(self, resource):
        if resource.scheme == "s3":
            return S3Loader(resource)

    def select_Control(self, type):
        if type == "aws":
            return AwsControl
