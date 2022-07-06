from typing import List
from dataclasses import dataclass
from .content import ContentError


@dataclass
class RowError(ContentError):
    """Row error representation"""

    code = "row-error"
    name = "Row Error"
    tags = ["#table", "content", "#row"]
    template = "Row Error"
    description = "Row Error"

    # State

    cells: List[str]
    """TODO: add docs"""

    row_number: int
    """TODO: add docs"""

    # Convert

    @classmethod
    def from_row(cls, row, *, note):
        """Create an error from a row

        Parameters:
            row (Row): row
            note (str): note

        Returns:
            RowError: error
        """
        to_str = lambda v: str(v) if v is not None else ""
        return cls(
            note=note,
            cells=list(map(to_str, row.cells)),
            row_number=row.row_number,
        )

    # Metadata

    metadata_profile = {
        "type": "object",
        "required": ["note"],
        "properties": {
            "code": {},
            "name": {},
            "tags": {},
            "description": {},
            "message": {},
            "note": {},
            "cells": {},
            "rowNumber": {},
        },
    }


class BlankRowError(RowError):
    code = "blank-row"
    name = "Blank Row"
    template = 'Row at position "{rowNumber}" is completely blank'
    description = "This row is empty. A row should contain at least one value."


class PrimaryKeyError(RowError):
    code = "primary-key"
    name = "PrimaryKey Error"
    template = 'Row at position "{rowNumber}" violates the primary key: {note}'
    description = "Values in the primary key fields should be unique for every row"


class ForeignKeyError(RowError):
    code = "foreign-key"
    name = "ForeignKey Error"
    template = 'Row at position "{rowNumber}" violates the foreign key: {note}'
    description = "Values in the foreign key fields should exist in the reference table"


class DuplicateRowError(RowError):
    code = "duplicate-row"
    name = "Duplicate Row"
    template = "Row at position {rowNumber} is duplicated: {note}"
    description = "The row is duplicated."


class RowConstraintError(RowError):
    code = "row-constraint"
    name = "Row Constraint"
    template = "The row at position {rowNumber} has an error: {note}"
    description = "The value does not conform to the row constraint."
