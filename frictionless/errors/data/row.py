from __future__ import annotations
import attrs
from typing import List
from .content import ContentError


@attrs.define(kw_only=True)
class RowError(ContentError):
    """Row error representation"""

    name = "Row Error"
    type = "row-error"
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
            "type": {},
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
    name = "Blank Row"
    type = "blank-row"
    template = 'Row at position "{rowNumber}" is completely blank'
    description = "This row is empty. A row should contain at least one value."


class PrimaryKeyError(RowError):
    name = "PrimaryKey Error"
    type = "primary-key"
    template = 'Row at position "{rowNumber}" violates the primary key: {note}'
    description = "Values in the primary key fields should be unique for every row"


class ForeignKeyError(RowError):
    name = "ForeignKey Error"
    type = "foreign-key"
    template = 'Row at position "{rowNumber}" violates the foreign key: {note}'
    description = "Values in the foreign key fields should exist in the reference table"


class DuplicateRowError(RowError):
    name = "Duplicate Row"
    type = "duplicate-row"
    template = "Row at position {rowNumber} is duplicated: {note}"
    description = "The row is duplicated."


class RowConstraintError(RowError):
    name = "Row Constraint"
    type = "row-constraint"
    template = "The row at position {rowNumber} has an error: {note}"
    description = "The value does not conform to the row constraint."
