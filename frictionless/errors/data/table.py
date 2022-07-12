from .data import DataError


class TableError(DataError):
    name = "Table Error"
    type = "table-error"
    tags = ["#table"]
    template = "General table error: {note}"
    description = "There is a table error."


class FieldCountError(TableError):
    name = "Field Count Error"
    type = "field-count"
    template = "The data source does not match the expected field count: {note}"
    description = "This error can happen if the data is corrupted."


class RowCountError(TableError):
    name = "Row Count Error"
    type = "row-count"
    template = "The data source does not match the expected row count: {note}"
    description = "This error can happen if the data is corrupted."


class TableDimensionsError(TableError):
    name = "Table dimensions error"
    type = "table-dimensions"
    template = "The data source does not have the required dimensions: {note}"
    description = "This error can happen if the data is corrupted."


class DeviatedValueError(TableError):
    name = "Deviated Value"
    type = "deviated-value"
    template = "There is a possible error because the value is deviated: {note}"
    description = "The value is deviated."


class DeviatedCellError(TableError):
    name = "Deviated cell"
    type = "deviated-cell"
    template = "There is a possible error because the cell is deviated: {note}"
    description = "The cell is deviated."
