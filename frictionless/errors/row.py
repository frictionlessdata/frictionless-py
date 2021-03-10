from .table import TableError


class RowError(TableError):
    """Row error representation

    Parameters:
        descriptor? (str|dict): error descriptor
        note (str): an error note
        row_number (int): row number
        row_position (int): row position

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    code = "row-error"
    name = "Row Error"
    tags = ["#table", "#row"]
    template = "Row Error"
    description = "Row Error"

    def __init__(self, descriptor=None, *, note, cells, row_number, row_position):
        self.setinitial("cells", cells)
        self.setinitial("rowNumber", row_number)
        self.setinitial("rowPosition", row_position)
        super().__init__(descriptor, note=note)

    # Create

    @classmethod
    def from_row(cls, row, *, note):
        """Create an error from a row

        Parameters:
            row (Row): row
            note (str): note

        Returns:
            RowError: error
        """
        return cls(
            note=note,
            cells=list(map(str, row)),
            row_number=row.row_number,
            row_position=row.row_position,
        )


class BlankRowError(RowError):
    code = "blank-row"
    name = "Blank Row"
    template = 'Row at position "{rowPosition}" is completely blank'
    description = "This row is empty. A row should contain at least one value."


class PrimaryKeyError(RowError):
    code = "primary-key-error"
    name = "PrimaryKey Error"
    template = 'Row at position "{rowPosition}" violates the primary key: {note}'
    description = "Values in the primary key fields should be unique for every row"


class ForeignKeyError(RowError):
    code = "foreign-key-error"
    name = "ForeignKey Error"
    template = 'Row at position "{rowPosition}" violates the foreign key: {note}'
    description = "Values in the foreign key fields should exist in the reference table"


class DuplicateRowError(RowError):
    code = "duplicate-row"
    name = "Duplicate Row"
    template = "Row at position {rowPosition} is duplicated: {note}"
    description = "The row is duplicated."


class RowConstraintError(RowError):
    code = "row-constraint"
    name = "Row Constraint"
    template = "The row at position {rowPosition} has an error: {note}"
    description = "The value does not conform to the row constraint."
