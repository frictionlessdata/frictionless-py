from __future__ import annotations
from ...records import PathDetails
from ...system import Plugin
from .control import BufferControl
from .loader import BufferLoader


class BufferPlugin(Plugin):
    """Plugin for Buffer Data"""

    # Hooks

    def create_loader(self, resource):
        if resource.scheme == "buffer":
            return BufferLoader(resource)

    def detect_path_details(self, details: PathDetails):
        if details.data is not None:
            if isinstance(details.data, bytes):
                details.scheme = "buffer"
        elif details.scheme == "buffer":
            details.data = b""

    def select_Control(self, type):
        if type == "buffer":
            return BufferControl
