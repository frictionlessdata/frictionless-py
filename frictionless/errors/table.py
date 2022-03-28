from ..error import Error


class TableError(Error):
    code = "table-error"
    name = "Table Error"
    tags = ["#table"]
    template = "General table error: {note}"
    description = "There is a table error."


class FieldCountError(TableError):
    code = "field-count-error"
    name = "Field Count Error"
    template = "The data source does not match the expected field count: {note}"
    description = "This error can happen if the data is corrupted."


class RowCountError(TableError):
    code = "row-count-error"
    name = "Row Count Error"
    template = "The data source does not match the expected row count: {note}"
    description = "This error can happen if the data is corrupted."


class TableDimensionsError(TableError):
    code = "table-dimensions-error"
    name = "Table dimensions error"
    template = "The data source does not have the required dimensions: {note}"
    description = "This error can happen if the data is corrupted."

    def __init__(self, note, limits):
        self.setinitial("limits", limits)
        super().__init__(note=note)


class DeviatedValueError(TableError):
    code = "deviated-value"
    name = "Deviated Value"
    template = "There is a possible error because the value is deviated: {note}"
    description = "The value is deviated."
