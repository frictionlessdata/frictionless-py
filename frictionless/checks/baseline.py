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
        # table
        errors.DialectError,
        errors.SchemaError,
        errors.FieldError,
        # header
        errors.ExtraLabelError,
        errors.MissingLabelError,
        errors.BlankLabelError,
        errors.DuplicateLabelError,
        errors.BlankHeaderError,
        errors.IncorrectLabelError,
        # content
        errors.ExtraCellError,
        errors.MissingCellError,
        errors.BlankRowError,
        errors.TypeError,
        errors.ConstraintError,
        errors.UniqueError,
        errors.PrimaryKeyError,
        errors.ForeignKeyError,
    ]

    # Validate

    # TODO: use something like table.empty here?
    # TODO: move source error to validate_source?
    def validate_schema(self, schema):
        yield from (
            schema.metadata_errors
            if self.table.header or self.table.sample
            else [errors.SourceError(note="the source is empty")]
        )

    def validate_header(self, header):
        yield from header.errors

    def validate_row(self, row):
        yield from row.errors

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "properties": {},
    }
