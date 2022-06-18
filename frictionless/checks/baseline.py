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

    # Connect

    def connect(self, resource):
        super().connect(resource)
        self.__stats = resource.stats.copy()

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
        hash = self.__stats.get("hash")
        bytes = self.__stats.get("bytes")
        fields = self.__stats.get("fields")
        rows = self.__stats.get("rows")

        # Hash
        if hash:
            hashing = self.resource.hashing
            if hash != self.resource.stats["hash"]:  # type: ignore
                note = 'expected %s is "%s" and actual is "%s"'
                note = note % (hashing, hash, self.resource.stats["hash"])  # type: ignore
                yield errors.HashCountError(note=note)

        # Bytes
        if bytes:
            if bytes != self.resource.stats["bytes"]:  # type: ignore
                note = 'expected is "%s" and actual is "%s"'
                note = note % (bytes, self.resource.stats["bytes"])  # type: ignore
                yield errors.ByteCountError(note=note)

        # Fields
        if fields:
            if fields != self.resource.stats["fields"]:  # type: ignore
                note = 'expected is "%s" and actual is "%s"'
                note = note % (fields, self.resource.stats["fields"])  # type: ignore
                yield errors.FieldCountError(note=note)

        # Rows
        if rows:
            if rows != self.resource.stats["rows"]:  # type: ignore
                note = 'expected is "%s" and actual is "%s"'
                note = note % (rows, self.resource.stats["rows"])  # type: ignore
                yield errors.RowCountError(note=note)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "properties": {},
    }
    metadata_properties = [
        {"name": "code"},
    ]
