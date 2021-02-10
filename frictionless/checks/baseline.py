from ..check import Check
from .. import errors


class baseline(Check):
    """Check a table for basic errors

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(...)`

    Ths check is enabled by default for any `validate` function run.

    """

    code = "baseline"
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

    def __init__(self, descriptor=None, *, stats=None):
        self.setinitial("stats", stats)
        super().__init__(descriptor)

    # Validate

    def validate_start(self):
        if self.resource.tabular:
            empty = not (self.resource.labels or self.resource.fragment)
            yield from [errors.SourceError(note="the source is empty")] if empty else []
            yield from self.resource.header.errors
        yield from []

    def validate_row(self, row):
        yield from row.errors

    def validate_end(self):
        stats = self.get("stats", {})

        # Hash
        if stats.get("hash"):
            hashing = self.resource.hashing
            if stats["hash"] != self.resource.stats["hash"]:
                note = 'expected %s is "%s" and actual is "%s"'
                note = note % (hashing, stats["hash"], self.resource.stats["hash"])
                yield errors.HashCountError(note=note)

        # Bytes
        if stats.get("bytes"):
            if stats["bytes"] != self.resource.stats["bytes"]:
                note = 'expected is "%s" and actual is "%s"'
                note = note % (stats["bytes"], self.resource.stats["bytes"])
                yield errors.ByteCountError(note=note)

        # Fields
        if stats.get("fields"):
            if stats["fields"] != self.resource.stats["fields"]:
                note = 'expected is "%s" and actual is "%s"'
                note = note % (stats["fields"], self.resource.stats["fields"])
                yield errors.FieldCountError(note=note)

        # Rows
        if stats.get("rows"):
            if stats["rows"] != self.resource.stats["rows"]:
                note = 'expected is "%s" and actual is "%s"'
                note = note % (stats["rows"], self.resource.stats["rows"])
                yield errors.RowCountError(note=note)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "properties": {
            "stats": {
                "type": "object",
                "properties": {
                    "hash": {"type": "string"},
                    "bytes": {"type": "number"},
                    "fields": {"type": "number"},
                    "rows": {"type": "number"},
                },
            }
        },
    }
