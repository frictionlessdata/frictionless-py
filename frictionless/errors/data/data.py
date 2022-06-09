from ..resource import ResourceError


class DataError(ResourceError):
    code = "data-error"
    name = "Data Error"
    tags = ["#data"]
    template = "Data error: {note}"
    description = "There is a data error."
