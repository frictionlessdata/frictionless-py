from __future__ import annotations
import attrs
from typing import List, Any
from .table import TableError


@attrs.define(kw_only=True)
class RowError(TableError):
    """Row error representation.

    A base class for all the errors related to a row of the
    tabular data.

    """

    type = "row-error"
    title = "Row Error"
    description = "Row Error"
    template = "Row Error"
    tags = ["#table", "#row"]

    # State

    cells: List[str]
    """
    Values of all the cells in the row that has an error.
    """

    row_number: int
    """
    Index of the row that has an error.
    """

    # Convert

    @classmethod
    def from_row(cls, row, *, note):
        """Create an error from a row"""
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
class ForeignKeyError(RowError):
    type = "foreign-key"
    title = "ForeignKey Error"
    description = "Values in the foreign key fields should exist in the reference table"
    template = 'Row at position "{rowNumber}" violates the foreign key: {note}'

    field_names: List[str]
    """
    Keys in the resource target column.
    """

    field_cells: List[str]
    """
    Cells not found in the lookup table.
    """

    reference_name: str
    """
    Name of the lookup table the keys were searched on
    """

    reference_field_names: List[str]
    """
    Key names in the lookup table defined as foreign keys in the resource.
    """

    @classmethod
    def from_row(
        cls,
        row,
        *,
        note,
        field_names: List[str],
        field_values: List[Any],
        reference_name: str,
        reference_field_names: List[str],
    ):
        """Create an foreign-key-error from a row"""
        to_str = lambda v: str(v) if v is not None else ""
        return cls(
            note=note,
            cells=list(map(to_str, row.cells)),
            row_number=row.row_number,
            field_names=field_names,
            field_cells=list(map(to_str, field_values)),
            reference_name=reference_name,
            reference_field_names=reference_field_names,
        )

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "fieldNames": {"type": "array", "items": {"type": "string"}},
            "fieldCells": {"type": "array", "items": {"type": "string"}},
            "referenceName": {"type": "string"},
            "referenceFieldNames": {"type": "array", "items": {"type": "string"}},
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
