from ..error import Error


class TableError(Error):
    code = "table-error"
    name = "Table Error"
    tags = ["#table"]
    template = "General table error: {note}"
    description = "There is a table error."


class ChecksumError(TableError):
    code = "checksum-error"
    name = "Checksum Error"
    tags = ["#table"]
    template = "The data source does not match the expected checksum: {note}"
    description = "This error can happen if the data is corrupted."


class DeviatedValueError(TableError):
    code = "deviated-value"
    name = "Deviated Value"
    tags = ["#table"]
    template = "There is a possible error because the value is deviated: {note}"
    description = "The value is deviated."
