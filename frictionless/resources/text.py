from __future__ import annotations
from typing import Optional, Union, Any
from ..platform import platform
from ..resource import Resource
from .. import helpers


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

    # Render

    def render_text(self, *, livemark: bool = False) -> str:
        assert self.normpath
        assert self.format == "md"
        if livemark:
            document = platform.livemark.Document(source=self.normpath)
            document.read()
            document.process()
            return document.output
        markdown = platform.marko.Markdown()
        markdown.use(platform.marko_ext_gfm.GFM)
        text = self.read_text()
        return markdown.convert(text)

    # Write

    # TODO: rebase on using loader
    def write_text(self, target: Optional[Union[TextResource, Any]] = None, **options):
        """Write text data to the target"""
        res = target
        if not isinstance(res, TextResource):
            if res:
                options["path"] = res
            res = TextResource(**options)
        text = self.read_text()
        bytes = text.encode(res.encoding or "utf-8")
        assert res.normpath
        helpers.write_file(res.normpath, bytes, mode="wb")
        return res
