from __future__ import annotations
import io
from ...system import Plugin
from ...records import PathDetails
from .control import StreamControl
from .loader import StreamLoader


class StreamPlugin(Plugin):
    """Plugin for Stream Data"""

    # Hooks

    def create_loader(self, resource):
        if resource.scheme == "stream":
            return StreamLoader(resource)

    def detect_path_details(self, details: PathDetails):
        if details.data is not None:
            if hasattr(details.data, "read"):
                details.scheme = "stream"
        elif details.scheme == "stream":
            details.data = io.BufferedRandom(io.BytesIO())  # type: ignore

    def select_Control(self, type):
        if type == "stream":
            return StreamControl
