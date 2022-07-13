from __future__ import annotations
import attrs
from ...exception import FrictionlessException
from .row import RowError


@attrs.define(kw_only=True)
class CellError(RowError):
    """Cell error representation"""

    name = "Cell Error"
    type = "cell-error"
    tags = ["#table", "#content", "#row", "#cell"]
    template = "Cell Error"
    description = "Cell Error"

    # State

    cell: str
    """TODO: add docs"""

    field_name: str
    """TODO: add docs"""

    field_number: int
    """TODO: add docs"""

    # Convert

    @classmethod
    def from_row(cls, row, *, note, field_name):
        """Create and error from a cell

        Parameters:
            row (Row): row
            note (str): note
            field_name (str): field name

        Returns:
            CellError: error
        """
        # This algorithm can be optimized by storing more information in a row
        # At the same time, this function should not be called very often
        for field_number, name in enumerate(row.field_names, start=1):
            if field_name == name:
                cell = row[field_name]
                to_str = lambda v: str(v) if v is not None else ""
                return cls(
                    note=note,
                    cells=list(map(to_str, row.cells)),
                    row_number=row.row_number,
                    cell=str(cell),
                    field_name=field_name,
                    field_number=field_number,
                )
        raise FrictionlessException(f"Field {field_name} is not in the row")

    # Metadata

    metadata_profile = {
        "type": "object",
        "required": ["note"],
        "properties": {
            "name": {},
            "type": {},
            "tags": {},
            "description": {},
            "message": {},
            "note": {},
            "cells": {},
            "rowNumber": {},
            "cell": {},
            "fieldName": {},
            "fieldNumber": {},
        },
    }


class ExtraCellError(CellError):
    name = "Extra Cell"
    type = "extra-cell"
    template = 'Row at position "{rowNumber}" has an extra value in field at position "{fieldNumber}"'
    description = "This row has more values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns."


class MissingCellError(CellError):
    name = "Missing Cell"
    type = "missing-cell"
    template = 'Row at position "{rowNumber}" has a missing cell in field "{fieldName}" at position "{fieldNumber}"'
    description = "This row has less values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns."


class TypeError(CellError):
    name = "Type Error"
    type = "type-error"
    template = 'Type error in the cell "{cell}" in row "{rowNumber}" and field "{fieldName}" at position "{fieldNumber}": {note}'
    description = "The value does not match the schema type and format for this field."


class ConstraintError(CellError):
    name = "Constraint Error"
    type = "constraint-error"
    template = 'The cell "{cell}" in row at position "{rowNumber}" and field "{fieldName}" at position "{fieldNumber}" does not conform to a constraint: {note}'
    description = "A field value does not conform to a constraint."


class UniqueError(CellError):
    name = "Unique Error"
    type = "unique-error"
    template = 'Row at position "{rowNumber}" has unique constraint violation in field "{fieldName}" at position "{fieldNumber}": {note}'
    description = "This field is a unique field but it contains a value that has been used in another row."


class TruncatedValueError(CellError):
    name = "Truncated Value"
    type = "truncated-value"
    template = "The cell {cell} in row at position {rowNumber} and field {fieldName} at position {fieldNumber} has an error: {note}"
    description = "The value is possible truncated."


class ForbiddenValueError(CellError):
    name = "Forbidden Value"
    type = "forbidden-value"
    template = "The cell {cell} in row at position {rowNumber} and field {fieldName} at position {fieldNumber} has an error: {note}"
    description = "The value is forbidden."


class SequentialValueError(CellError):
    name = "Sequential Value"
    type = "sequential-value"
    template = "The cell {cell} in row at position {rowNumber} and field {fieldName} at position {fieldNumber} has an error: {note}"
    description = "The value is not sequential."


class AsciiValueError(CellError):
    name = "Ascii Value"
    type = "ascii-value"
    template = "The cell {cell} in row at position {rowNumber} and field {fieldName} at position {fieldNumber} has an error: {note}"
    description = "The cell contains non-ascii characters."
