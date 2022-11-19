from __future__ import annotations
from ...system import Plugin
from .control import MultipartControl
from .loader import MultipartLoader


class MultipartPlugin(Plugin):
    """Plugin for Multipart Data"""

    # Hooks

    def create_loader(self, resource):
        if resource.scheme == "multipart":
            return MultipartLoader(resource)

    def detect_resource(self, resource):
        if resource.multipart:
            resource.scheme = "multipart"

    def select_Control(self, type):
        if type == "multipart":
            return MultipartControl
