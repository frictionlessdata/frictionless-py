from __future__ import annotations
from ...system import Plugin
from .control import LocalControl
from .loader import LocalLoader


class LocalPlugin(Plugin):
    """Plugin for Local Data"""

    # Hooks

    def create_loader(self, resource):
        if resource.scheme == "file":
            return LocalLoader(resource)

    def select_Control(self, type):
        if type == "local":
            return LocalControl
