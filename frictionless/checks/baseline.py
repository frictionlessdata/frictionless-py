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
    ]

    # Validate

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

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "properties": {},
    }
