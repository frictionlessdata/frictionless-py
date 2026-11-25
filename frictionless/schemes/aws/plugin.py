from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional
from urllib.parse import urlparse

from ...system import Plugin
from .adapter import AwsAdapter
from .control import AwsControl
from .loaders import S3Loader

if TYPE_CHECKING:
    from ...dialect import Control
    from ...resource import Resource
    from ...system import Loader


class AwsPlugin(Plugin):
    """Plugin for Aws"""

    # Hooks

    def create_adapter(
        self,
        source: Any,
        *,
        control: Optional[Control] = None,
        basepath: Optional[str] = None,
        packagify: bool = False,
    ):
        if isinstance(source, str):
            parsed = urlparse(source)
            if parsed.scheme == "s3":
                return AwsAdapter(source=source, basepath=basepath)

    def create_loader(self, resource: Resource) -> Optional[Loader]:
        if resource.scheme == "s3":
            return S3Loader(resource)

    def select_control_class(self, type: Optional[str] = None):
        if type == "aws":
            return AwsControl
