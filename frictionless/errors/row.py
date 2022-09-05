from __future__ import annotations
import attrs
from typing import List, Iterable

from frictionless.table.row import Row
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


class ForeignKeyError(RowError):
    type = "foreign-key"
    title = "ForeignKey Error"
    description = "Values in the foreign key fields should exist in the reference table"
    template = 'Row at position "{rowNumber}" violates the foreign key: {note}'

    target_keys: Iterable
    """
    Keys in the resource target column.
    """
    source_keys: Iterable
    """
    Key names in the lookup table defined as foreign keys in the resource.
    """

    source_name: str
    """
    Name of the lookup table the keys were searched on
    """

    missing_values: Iterable
    """
    Cell values not found in the lookup table.
    """

    @classmethod
    def from_row(
        cls,
        row: Row,
        *,
        target_keys: Iterable,
        source_keys: Iterable,
        source_name: str,
        missing_values: Iterable,
        note: str,
    ):
        """Create an foreign-key-error from a row

        Parameters:
            row: row
            target_keys: target keys
            source_keys: source keys
            source_name: source name
            missing_values: values from the source not found in the target.
            note: note

        Returns:
            ForeignKeyError: error
        """
        cls = super().from_row(row=row, note=note)
        cls.row_number = row.row_number
        cls.target_keys = target_keys
        cls.source_keys = source_keys
        cls.source_name = source_name
        cls.missing_values = missing_values
        return cls

    # Metadata

    metadata_profile_patch = {
        "properties": {
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
