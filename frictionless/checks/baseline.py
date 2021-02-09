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
        # Table
        errors.ChecksumError,
    ]

    def __init__(self, descriptor=None, *, stats=None):
        self.setinitial("stats", stats)
        super().__init__(descriptor)

    # Validate

    # TODO: rename to validate_start?
    def validate_source(self):
        empty = not (self.resource.sample or self.resource.labels)
        yield from [errors.SourceError(note="the source is empty")] if empty else []

    def validate_schema(self):
        empty = not (self.resource.sample or self.resource.labels)
        yield from self.resource.schema.metadata_errors if not empty else []

    def validate_header(self):
        yield from self.resource.header.errors

    def validate_row(self, row):
        yield from row.errors

    # TODO: rename to validate_end?
    def validate_table(self):
        stats = self.get("stats", {})

        # Hash
        if stats.get("hash"):
            hashing = self.resource.hashing
            if stats["hash"] != self.resource.stats["hash"]:
                note = 'expected hash in %s is "%s" and actual is "%s"'
                note = note % (hashing, stats["hash"], self.resource.stats["hash"])
                yield errors.ChecksumError(note=note)

        # Bytes
        if stats.get("bytes"):
            if stats["bytes"] != self.resource.stats["bytes"]:
                note = 'expected bytes count is "%s" and actual is "%s"'
                note = note % (stats["bytes"], self.resource.stats["bytes"])
                yield errors.ChecksumError(note=note)

        # Fields
        if stats.get("fields"):
            if stats["fields"] != self.resource.stats["fields"]:
                note = 'expected fields count is "%s" and actual is "%s"'
                note = note % (stats["fields"], self.resource.stats["fields"])
                yield errors.ChecksumError(note=note)

        # Rows
        if stats.get("rows"):
            if stats["rows"] != self.resource.stats["rows"]:
                note = 'expected rows count is "%s" and actual is "%s"'
                note = note % (stats["rows"], self.resource.stats["rows"])
                yield errors.ChecksumError(note=note)

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
