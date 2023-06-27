from __future__ import annotations

from typing import Any, Optional, Union

from .. import helpers
from ..exception import FrictionlessException
from ..resource import Resource


class TextResource(Resource):
    type = "text"
    datatype = "text"

    # Read

    # TODO: rebase on using loader
    def read_text(self, *, size: Optional[int] = None) -> str:
        """Read text into memory

        Returns:
            str: resource text
        """
        if self.memory:
            return str(self.data)
        with helpers.ensure_open(self):
            return self.text_stream.read(size)  # type: ignore

    # Write

    # TODO: rebase on using loader
    def write_text(
        self, target: Optional[Union[TextResource, Any]] = None, **options: Any
    ):
        """Write text data to the target"""
        resource = target
        if not isinstance(resource, Resource):
            resource = TextResource(**options)
        if not isinstance(resource, TextResource):  # type: ignore
            raise FrictionlessException("target must be a text resource")
        text = self.read_text()
        bytes = text.encode(resource.encoding or "utf-8")
        assert resource.normpath
        helpers.write_file(resource.normpath, bytes, mode="wb")
        return resource


class ArticleResource(TextResource):
    datatype = "article"


class ScriptResource(TextResource):
    datatype = "script"
