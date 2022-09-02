from __future__ import annotations
from ..error import Error


class DataError(Error):
    type = "data-error"
    title = "Data Error"
    description = "There is a data error."
    template = "Data error: {note}"
