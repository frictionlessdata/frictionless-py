from ..check import Check
from .. import errors


class BaselineCheck(Check):
    """Check a table for basic errors

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(...)`

    Ths check is enabled by default for any `validate` function run.

    """

    possible_Errors = [  # type: ignore
        # table
        errors.DialectError,
        errors.SchemaError,
        errors.FieldError,
        # head
        errors.ExtraHeaderError,
        errors.MissingHeaderError,
        errors.BlankHeaderError,
        errors.DuplicateHeaderError,
        errors.NonMatchingHeaderError,
        # body
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

    def validate_schema(self, schema):
        yield from schema.metadata_errors if self.table.sample else [
            errors.SchemaError(note="there is no data available")
        ]

    def validate_header(self, header):
        yield from header.errors

    def validate_row(self, row):
        yield from row.errors

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    }
