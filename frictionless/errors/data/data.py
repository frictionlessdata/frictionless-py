from ...error import Error


class DataError(Error):
    code = "data-error"
    name = "Data Error"
    template = "Data error: {note}"
    description = "There is a data error."
