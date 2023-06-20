from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ...system import Plugin
from .control import AwsControl
from .loaders import S3Loader

if TYPE_CHECKING:
    from ...resource import Resource
    from ...system import Loader


class AwsPlugin(Plugin):
    """Plugin for Aws"""

    # Hooks

    def create_loader(self, resource: Resource) -> Optional[Loader]:
        if resource.scheme == "s3":
            return S3Loader(resource)

    def select_control_class(self, type: Optional[str] = None):
        if type == "aws":
            return AwsControl
