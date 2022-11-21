from __future__ import annotations
import typing
from ...system import Plugin
from .control import InlineControl
from .parser import InlineParser


class InlinePlugin(Plugin):
    """Plugin for Inline"""

    # Hooks

    def create_parser(self, resource):
        if resource.format == "inline":
            return InlineParser(resource)

    def detect_resource(self, resource):
        if resource.data is not None:
            if not hasattr(resource.data, "read"):
                types = (list, typing.Iterator, typing.Generator)
                if callable(resource.data) or isinstance(resource.data, types):
                    resource.type = "table"
                    resource.scheme = ""
                    resource.format = "inline"
                    resource.mediatype = "application/inline"
        elif resource.format == "inline":
            resource.data = []

    def select_Control(self, type):
        if type == "inline":
            return InlineControl
