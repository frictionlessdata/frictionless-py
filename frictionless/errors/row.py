from __future__ import annotations
import attrs
from typing import List
from .table import TableError


@attrs.define(kw_only=True)
class RowError(TableError):
    """Row error representation"""

    type = "row-error"
    title = "Row Error"
    description = "Row Error"
    template = "Row Error"
    tags = ["#table", "#row"]

    # State

    cells: List[str]
    """NOTE: add docs"""

    row_number: int
    """NOTE: add docs"""

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

    metadata_profile_patch = {
        "properties": {
            "cells": {"type": "array", "items": {"type": "string"}},
            "rowNumber": {"type": "integer"},
        },
    }


class BlankRowError(RowError):
    type = "blank-row"
    title = "Blank Row"
    description = "This row is empty. A row should contain at least one value."
    template = 'Row at position "{rowNumber}" is completely blank'


class PrimaryKeyError(RowError):
    type = "primary-key"
    title = "PrimaryKey Error"
    description = "Values in the primary key fields should be unique for every row"
    template = 'Row at position "{rowNumber}" violates the primary key: {note}'


@attrs.define(kw_only=True)
class ForeignKeyError(TableError):
    type = "foreign-key"
    title = "ForeignKey Error"
    description = "Values in the foreign key fields should exist in the reference table"
    template = 'Row at position "{rowNumber}" violates the foreign key: {note}'
    tags = ["#table", "#row"]

    cells: List[str]
    """NOTE: add docs"""

    row_number: int
    """NOTE: add docs"""

    target_keys: List[str]
    """NOTE: add docs"""

    source_keys: List[int]
    """NOTE: add docs"""

    source_name: List[str]
    """NOTE: add docs"""

    missing_values: List[int]
    """NOTE: add docs"""

    @classmethod
    def from_row(
        cls, row, *, target_keys, source_keys, source_name, missing_values, note
    ):
        """Create an foreign-key-error from a row

        Parameters:
            row (Row): row
            target_keys (tuple): target keys
            source_keys (tuple): source keys
            source_name: (str): source name
            missing_values (tuple): missing values
            note (str): note

        Returns:
            ForeignKeyError: error
        """
        to_str = lambda v: str(v) if v is not None else ""
        return cls(
            note=note,
            cells=list(map(to_str, row.cells)),
            row_number=row.row_number,
            target_keys=target_keys,
            source_keys=source_keys,
            source_name=source_name,
            missing_values=missing_values,
        )

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "cells": {"type": "array", "items": {"type": "string"}},
            "rowNumber": {"type": "integer"},
            "targetKeys": {"type": "array", "items": {"type": "string"}},
            "sourceKeys": {"type": "array", "items": {"type": "string"}},
            "sourceName": {"type": "string"},
            "missingValues": {"type": "array", "items": {"type": "integer"}},
        },
    }


class DuplicateRowError(RowError):
    type = "duplicate-row"
    title = "Duplicate Row"
    description = "The row is duplicated."
    template = "Row at position {rowNumber} is duplicated: {note}"


class RowConstraintError(RowError):
    type = "row-constraint"
    title = "Row Constraint"
    description = "The value does not conform to the row constraint."
    template = "The row at position {rowNumber} has an error: {note}"
