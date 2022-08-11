from __future__ import annotations
import attrs
from ..checklist import Check
from .. import errors


@attrs.define(kw_only=True)
class baseline(Check):
    """Check a table for basic errors

    Ths check is enabled by default for any `validate` function run.

    """

    type = "baseline"
    Errors = [
        # File
        errors.Md5CountError,
        errors.Sha256CountError,
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

    def connect(self, resource):
        super().connect(resource)
        self.__stats = resource.stats.to_descriptor()

    # Validate

    def validate_start(self):
        if self.resource.tabular:
            empty = not (self.resource.labels or self.resource.fragment)
            yield from [errors.SourceError(note="the source is empty")] if empty else []
            yield from self.resource.header.errors  # type: ignore
        yield from []

    def validate_row(self, row):
        yield from row.errors  # type: ignore

    def validate_end(self):
        md5 = self.__stats.get("md5")
        sha256 = self.__stats.get("sha256")
        bytes = self.__stats.get("bytes")
        fields = self.__stats.get("fields")
        rows = self.__stats.get("rows")

        # Md5
        if md5:
            if md5 != self.resource.stats.md5:
                note = 'expected is "%s" and actual is "%s"'
                note = note % (md5, self.resource.stats.md5)
                yield errors.Md5CountError(note=note)

        # Sha256
        if sha256:
            if sha256 != self.resource.stats.sha256:
                note = 'expected is "%s" and actual is "%s"'
                note = note % (sha256, self.resource.stats.sha256)
                yield errors.Sha256CountError(note=note)

        # Bytes
        if bytes:
            if bytes != self.resource.stats.bytes:
                note = 'expected is "%s" and actual is "%s"'
                note = note % (bytes, self.resource.stats.bytes)
                yield errors.ByteCountError(note=note)

        # Fields
        if fields:
            if fields != self.resource.stats.fields:
                note = 'expected is "%s" and actual is "%s"'
                note = note % (fields, self.resource.stats.fields)
                yield errors.FieldCountError(note=note)

        # Rows
        if rows:
            if rows != self.resource.stats.rows:
                note = 'expected is "%s" and actual is "%s"'
                note = note % (rows, self.resource.stats.rows)
                yield errors.RowCountError(note=note)
