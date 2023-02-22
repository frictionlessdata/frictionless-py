from __future__ import annotations
import typing
from ...records import PathDetails
from ...system import Plugin
from .control import InlineControl
from .parser import InlineParser


class InlinePlugin(Plugin):
    """Plugin for Inline"""

    # Hooks

    def create_parser(self, resource):
        if resource.format == "inline":
            return InlineParser(resource)

    def detect_path_details(self, details: PathDetails):
        if details.data is not None:
            if not hasattr(details.data, "read"):
                types = (list, typing.Iterator, typing.Generator)
                if callable(details.data) or isinstance(details.data, types):
                    details.type = "table"
                    details.scheme = ""
                    details.format = "inline"
                    details.mediatype = "application/inline"
        elif details.format == "inline":
            details.data = []

    def select_Control(self, type):
        if type == "inline":
            return InlineControl
