from __future__ import annotations
from ...system import Plugin
from .control import LocalControl
from .loader import LocalLoader
from ... import helpers


class LocalPlugin(Plugin):
    """Plugin for Local Data"""

    # Hooks

    def create_loader(self, resource):
        if resource.scheme == "file":
            if not helpers.is_remote_path(resource.basepath or ""):
                return LocalLoader(resource)

    def select_Control(self, type):
        if type == "local":
            return LocalControl
