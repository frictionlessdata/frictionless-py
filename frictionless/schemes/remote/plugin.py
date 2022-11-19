from __future__ import annotations
from ...system import Plugin
from .control import RemoteControl
from .loader import RemoteLoader
from . import settings


class RemotePlugin(Plugin):
    """Plugin for Remote Data"""

    # Hooks

    def create_loader(self, resource):
        if resource.scheme in settings.DEFAULT_SCHEMES:
            return RemoteLoader(resource)

    def select_Control(self, type):
        if type == "remote":
            return RemoteControl
