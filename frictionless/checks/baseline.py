from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

import attrs

from .. import errors, helpers
from ..checklist import Check
from ..platform import platform

if TYPE_CHECKING:
    from ..error import Error
    from ..resource import Resource
    from ..table import Row


@attrs.define(kw_only=True, repr=False)
class baseline(Check):
    """Check a table for basic errors

    Ths check is enabled by default for any `validate` function run.

    """

    type = "baseline"
    Errors = [
        # File
        errors.HashCountError,
        errors.ByteCountError,
        # Table
        errors.FieldCountError,
        errors.RowCountError,
        # Header
        errors.BlankHeaderError,
        # Label
        errors.ExtraLabelError,
        errors.MissingLabelError,
        errors.BlankLabelError,
        errors.DuplicateLabelError,
        errors.IncorrectLabelError,
        # Row
        errors.BlankRowError,
        errors.PrimaryKeyError,
        errors.ForeignKeyError,
        # Cell
        errors.ExtraCellError,
        errors.MissingCellError,
        errors.TypeError,
        errors.ConstraintError,
        errors.UniqueError,
    ]

    # Connect

    def connect(self, resource: Resource):
        super().connect(resource)

    # Validate

    def validate_start(self) -> Iterable[Error]:
        if isinstance(self.resource, platform.frictionless_resources.TableResource):
            empty = not (self.resource.labels or self.resource.fragment)
            yield from [errors.SourceError(note="the source is empty")] if empty else []
            yield from self.resource.header.errors  # type: ignore
        yield from []

    def validate_row(self, row: Row) -> Iterable[Error]:
        yield from row.errors  # type: ignore

    def validate_end(self) -> Iterable[Error]:
        # Hash
        if self.resource.hash:
            algorithm, expected = helpers.parse_resource_hash_v1(self.resource.hash)
            actual = None
            if algorithm == "md5":
                actual = self.resource.stats.md5
            elif algorithm == "sha256":
                actual = self.resource.stats.sha256
            if actual and actual != expected:
                note = 'expected is "%s" and actual is "%s"'
                note = note % (expected, actual)
                yield errors.HashCountError(note=note)

        # Bytes
        if self.resource.bytes:
            if self.resource.bytes != self.resource.stats.bytes:
                note = 'expected is "%s" and actual is "%s"'
                note = note % (self.resource.bytes, self.resource.stats.bytes)
                yield errors.ByteCountError(note=note)

        # Fields
        if self.resource.fields:
            if self.resource.fields != self.resource.stats.fields:
                note = 'expected is "%s" and actual is "%s"'
                note = note % (self.resource.fields, self.resource.stats.fields)
                yield errors.FieldCountError(note=note)

        # Rows
        if self.resource.rows:
            if self.resource.rows != self.resource.stats.rows:
                note = 'expected is "%s" and actual is "%s"'
                note = note % (self.resource.rows, self.resource.stats.rows)
                yield errors.RowCountError(note=note)
