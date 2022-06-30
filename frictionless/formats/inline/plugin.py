import typing
from ...plugin import Plugin
from .control import InlineControl
from .parser import InlineParser


class InlinePlugin(Plugin):
    """Plugin for Inline"""

    code = "inline"

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "inline":
            return InlineControl.from_descriptor(descriptor)

    def create_file(self, file):
        if not file.scheme and not file.format and file.memory:
            if not hasattr(file.data, "read"):
                types = (list, typing.Iterator, typing.Generator)
                if callable(file.data) or isinstance(file.data, types):
                    file.scheme = ""
                    file.format = "inline"
                    return file

    def create_parser(self, resource):
        if resource.format == "inline":
            return InlineParser(resource)
