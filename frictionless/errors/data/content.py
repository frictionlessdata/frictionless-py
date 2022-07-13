from __future__ import annotations
from .table import TableError


class ContentError(TableError):
    name = "Content Error"
    type = "content-error"
    tags = ["#table" "#content"]
    template = "Content error: {note}"
    description = "There is a content error."
