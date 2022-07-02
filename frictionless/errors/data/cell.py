from dataclasses import dataclass
from ...exception import FrictionlessException
from .row import RowError


@dataclass
class CellError(RowError):
    """Cell error representation"""

    code = "cell-error"
    name = "Cell Error"
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


class ExtraCellError(CellError):
    code = "extra-cell"
    name = "Extra Cell"
    template = 'Row at position "{rowPosition}" has an extra value in field at position "{fieldPosition}"'
    description = "This row has more values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns."


class MissingCellError(CellError):
    code = "missing-cell"
    name = "Missing Cell"
    template = 'Row at position "{rowPosition}" has a missing cell in field "{fieldName}" at position "{fieldPosition}"'
    description = "This row has less values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns."


class TypeError(CellError):
    code = "type-error"
    name = "Type Error"
    template = 'Type error in the cell "{cell}" in row "{rowPosition}" and field "{fieldName}" at position "{fieldPosition}": {note}'
    description = "The value does not match the schema type and format for this field."


class ConstraintError(CellError):
    code = "constraint-error"
    name = "Constraint Error"
    template = 'The cell "{cell}" in row at position "{rowPosition}" and field "{fieldName}" at position "{fieldPosition}" does not conform to a constraint: {note}'
    description = "A field value does not conform to a constraint."


class UniqueError(CellError):
    code = "unique-error"
    name = "Unique Error"
    template = 'Row at position "{rowPosition}" has unique constraint violation in field "{fieldName}" at position "{fieldPosition}": {note}'
    description = "This field is a unique field but it contains a value that has been used in another row."


class TruncatedValueError(CellError):
    code = "truncated-value"
    name = "Truncated Value"
    template = "The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has an error: {note}"
    description = "The value is possible truncated."


class ForbiddenValueError(CellError):
    code = "forbidden-value"
    name = "Forbidden Value"
    template = "The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has an error: {note}"
    description = "The value is forbidden."


class SequentialValueError(CellError):
    code = "sequential-value"
    name = "Sequential Value"
    template = "The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has an error: {note}"
    description = "The value is not sequential."


class AsciiValueError(CellError):
    code = "ascii-value"
    name = "Ascii Value"
    template = "The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has an error: {note}"
    description = "The cell contains non-ascii characters."
