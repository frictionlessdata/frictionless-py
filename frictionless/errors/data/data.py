from ...error import Error


class DataError(Error):
    name = "Data Error"
    type = "data-error"
    template = "Data error: {note}"
    description = "There is a data error."
