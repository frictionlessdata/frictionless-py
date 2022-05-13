from ... import errors
from ...check import Check
from typing import Iterator


class ascii_value(Check):
    """Check whether all the string characters in the data are ASCII

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(checks=[{"code": "ascii-value"}])`

    This check can be enabled using the `checks` parameter
    for the `validate` function.

    """

    code = "ascii-value"
    Errors = [errors.AsciiValueError]

    # Validate

    def validate_row(self, row: any) -> Iterator[any]:
        for field in row.fields:
            if field.type == "string":
                cell = row[field.name]
                if cell and not cell.isascii():
                    note = "the cell contains non-ascii characters"
                    yield errors.AsciiValueError.from_row(
                        row, note=note, field_name=field.name
                    )

    # Metadata

    metadata_profile = {
        "type": "object",
        "properties": {},
    }
