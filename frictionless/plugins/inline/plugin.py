import typing
from ...plugin import Plugin
from .dialect import InlineDialect
from .parser import InlineParser


class InlinePlugin(Plugin):
    """Plugin for Inline

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.inline import InlinePlugin`

    """

    code = "inline"

    def create_file(self, file):
        if not file.scheme and not file.format and file.memory:
            if not hasattr(file.data, "read"):
                types = (list, typing.Iterator, typing.Generator)
                if callable(file.data) or isinstance(file.data, types):
                    file.scheme = ""
                    file.format = "inline"
                    return file

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "inline":
            return InlineDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "inline":
            return InlineParser(resource)
