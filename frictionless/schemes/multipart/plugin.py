from __future__ import annotations
from typing import TYPE_CHECKING
from ...system import Plugin
from .control import MultipartControl
from .loader import MultipartLoader

if TYPE_CHECKING:
    from ...resource import Resource


class MultipartPlugin(Plugin):
    """Plugin for Multipart Data"""

    # Hooks

    def create_loader(self, resource):
        if resource.scheme == "multipart":
            return MultipartLoader(resource)

    def detect_resource(self, resource: Resource):
        if resource.extrapaths:
            resource.scheme = "multipart"

    def select_control_class(self, type):
        if type == "multipart":
            return MultipartControl
