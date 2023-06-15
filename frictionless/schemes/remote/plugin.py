from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from ...system import Plugin
from .control import RemoteControl
from .loader import RemoteLoader
from ... import helpers
from . import settings

if TYPE_CHECKING:
    from ...resource import Resource
    from ...system import Loader


class RemotePlugin(Plugin):
    """Plugin for Remote Data"""

    # Hooks

    def create_loader(self, resource: Resource) -> Optional[Loader]:
        if helpers.is_remote_path(resource.basepath or ""):
            return RemoteLoader(resource)
        if resource.scheme in settings.DEFAULT_SCHEMES:
            return RemoteLoader(resource)

    def select_control_class(self, type: Optional[str] = None):
        if type == "remote":
            return RemoteControl
