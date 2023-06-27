from __future__ import annotations

from ...platform import platform


def render_article(text: str) -> str:
    markdown = platform.marko.Markdown()
    markdown.use(platform.marko_ext_gfm.GFM)
    return markdown.convert(text)
