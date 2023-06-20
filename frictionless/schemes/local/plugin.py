from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from ... import helpers
from ...system import Plugin
from .adapter import LocalAdapter
from .control import LocalControl
from .loader import LocalLoader

if TYPE_CHECKING:
    from ...dialect import Control
    from ...resource import Resource
    from ...system import Loader


class LocalPlugin(Plugin):
    """Plugin for Local Data"""

    # Hooks

    def create_adapter(
        self,
        source: Any,
        *,
        control: Optional[Control] = None,
        basepath: Optional[str] = None,
        packagify: bool = False,
    ):
        if source is not None:
            path = source
            if isinstance(source, str):
                path = helpers.join_basepath(source, basepath=basepath)
            if helpers.is_directory_source(path) or helpers.is_expandable_source(path):
                return LocalAdapter(source, basepath=basepath)

    def create_loader(self, resource: Resource) -> Optional[Loader]:
        if resource.scheme == "file":
            if not helpers.is_remote_path(resource.basepath or ""):
                return LocalLoader(resource)

    def select_control_class(self, type: Optional[str] = None):
        if type == "local":
            return LocalControl
