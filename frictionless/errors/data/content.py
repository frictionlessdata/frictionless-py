from __future__ import annotations
from .table import TableError


class ContentError(TableError):
    type = "content-error"
    title = "Content Error"
    description = "There is a content error."
    template = "Content error: {note}"
    tags = ["#table" "#content"]
