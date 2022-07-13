from __future__ import annotations
import typing
from ...plugin import Plugin
from .control import InlineControl
from .parser import InlineParser


class InlinePlugin(Plugin):
    """Plugin for Inline"""

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("type") == "inline":
            return InlineControl.from_descriptor(descriptor)

    def create_parser(self, resource):
        if resource.format == "inline":
            return InlineParser(resource)

    def detect_resource(self, resource):
        if resource.data is not None:
            if not hasattr(resource.data, "read"):
                resource.type = "table"
                types = (list, typing.Iterator, typing.Generator)
                if callable(resource.data) or isinstance(resource.data, types):
                    resource.scheme = ""
                    resource.format = "inline"
                    resource.mediatype = "application/inline"
