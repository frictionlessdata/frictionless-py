from __future__ import annotations
from .data import DataError


class TableError(DataError):
    type = "table-error"
    title = "Table Error"
    description = "There is a table error."
    template = "General table error: {note}"
    tags = ["#table"]


class FieldCountError(TableError):
    type = "field-count"
    title = "Field Count Error"
    description = "This error can happen if the data is corrupted."
    template = "The data source does not match the expected field count: {note}"


class RowCountError(TableError):
    type = "row-count"
    title = "Row Count Error"
    description = "This error can happen if the data is corrupted."
    template = "The data source does not match the expected row count: {note}"


class TableDimensionsError(TableError):
    type = "table-dimensions"
    title = "Table dimensions error"
    description = "This error can happen if the data is corrupted."
    template = "The data source does not have the required dimensions: {note}"


class DeviatedValueError(TableError):
    type = "deviated-value"
    title = "Deviated Value"
    description = "The value is deviated."
    template = "There is a possible error because the value is deviated: {note}"


class DeviatedCellError(TableError):
    type = "deviated-cell"
    title = "Deviated cell"
    description = "The cell is deviated."
    template = "There is a possible error because the cell is deviated: {note}"


class RequiredValueError(TableError):
    type = "required-value"
    title = "Required Value"
    description = "The required values are missing."
    template = "Required values not found: {note}"
