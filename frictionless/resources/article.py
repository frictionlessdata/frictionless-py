from __future__ import annotations

from typing import Optional

from ..platform import platform
from .text import TextResource


class ArticleResource(TextResource):
    datatype = "article"

    # Render

    def render_article(self, *, rich: Optional[bool] = None) -> str:
        if rich:
            assert self.normpath
            assert self.format == "md"
            document = platform.livemark.Document(source=self.normpath)
            document.read()
            document.process()
            return document.output  # type: ignore
        markdown = platform.marko.Markdown()
        markdown.use(platform.marko_ext_gfm.GFM)
        text = self.read_text()
        return markdown.convert(text)
