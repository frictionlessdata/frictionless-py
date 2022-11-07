from __future__ import annotations
import attrs
from ..exception import FrictionlessException
from .row import RowError


@attrs.define(kw_only=True)
class CellError(RowError):
    """Cell error representation.

    A base class for all the errors related to the cell value.
    """

    type = "cell-error"
    title = "Cell Error"
    description = "Cell Error"
    template = "Cell Error"
    tags = ["#table", "#row", "#cell"]

    # State

    cell: str
    """
    Cell where the error occurred.
    """

    field_name: str
    """
    Name of the field that has an error.
    """

    field_number: int
    """
    Index of the field that has an error.
    """

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

    metadata_profile_patch = {
        "properties": {
            "cell": {"type": "string"},
            "fieldName": {"type": "string"},
            "fieldNumber": {"type": "integer"},
        },
    }


class ExtraCellError(CellError):
    type = "extra-cell"
    title = "Extra Cell"
    description = "This row has more values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns."
    template = 'Row at position "{rowNumber}" has an extra value in field at position "{fieldNumber}"'


class MissingCellError(CellError):
    type = "missing-cell"
    title = "Missing Cell"
    description = "This row has less values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns."
    template = 'Row at position "{rowNumber}" has a missing cell in field "{fieldName}" at position "{fieldNumber}"'


class TypeError(CellError):
    type = "type-error"
    title = "Type Error"
    description = "The value does not match the schema type and format for this field."
    template = 'Type error in the cell "{cell}" in row "{rowNumber}" and field "{fieldName}" at position "{fieldNumber}": {note}'


class ConstraintError(CellError):
    type = "constraint-error"
    title = "Constraint Error"
    description = "A field value does not conform to a constraint."
    template = 'The cell "{cell}" in row at position "{rowNumber}" and field "{fieldName}" at position "{fieldNumber}" does not conform to a constraint: {note}'


class UniqueError(CellError):
    type = "unique-error"
    title = "Unique Error"
    description = "This field is a unique field but it contains a value that has been used in another row."
    template = 'Row at position "{rowNumber}" has unique constraint violation in field "{fieldName}" at position "{fieldNumber}": {note}'


class TruncatedValueError(CellError):
    type = "truncated-value"
    title = "Truncated Value"
    description = "The value is possible truncated."
    template = "The cell {cell} in row at position {rowNumber} and field {fieldName} at position {fieldNumber} has an error: {note}"


class ForbiddenValueError(CellError):
    type = "forbidden-value"
    title = "Forbidden Value"
    description = "The value is forbidden."
    template = "The cell {cell} in row at position {rowNumber} and field {fieldName} at position {fieldNumber} has an error: {note}"


class SequentialValueError(CellError):
    type = "sequential-value"
    title = "Sequential Value"
    description = "The value is not sequential."
    template = "The cell {cell} in row at position {rowNumber} and field {fieldName} at position {fieldNumber} has an error: {note}"


class AsciiValueError(CellError):
    type = "ascii-value"
    title = "Ascii Value"
    description = "The cell contains non-ascii characters."
    template = "The cell {cell} in row at position {rowNumber} and field {fieldName} at position {fieldNumber} has an error: {note}"
