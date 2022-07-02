from .table import TableError


class ContentError(TableError):
    code = "content-error"
    name = "Content Error"
    tags = ["#table" "#content"]
    template = "Content error: {note}"
    description = "There is a content error."
