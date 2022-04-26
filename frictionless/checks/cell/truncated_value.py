from ... import errors
from ...check import Check


class truncated_value(Check):
    """Check for possible truncated values

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(checks=([{"code": "truncated-value"}])`

    This check can be enabled using the `checks` parameter
    for the `validate` function.

    """

    code = "truncated-value"
    Errors = [errors.TruncatedValueError]

    def validate_row(self, row):
        for field_name, cell in row.items():
            truncated = False
            if cell is None:
                continue

            # Check string cutoff
            if isinstance(cell, str):
                if len(cell) in TRUNCATED_STRING_LENGTHS:
                    truncated = True

            # Check integer cutoff
            if isinstance(cell, int):
                if cell in TRUNCATED_INTEGER_VALUES:
                    truncated = True

            # Add error
            if truncated:
                note = "value  is probably truncated"
                yield errors.TruncatedValueError.from_row(
                    row, note=note, field_name=field_name
                )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "properties": {},
    }


# Internal


TRUNCATED_STRING_LENGTHS = [
    255,
]
TRUNCATED_INTEGER_VALUES = [
    # BigInt
    18446744073709551616,
    9223372036854775807,
    # Int
    4294967295,
    2147483647,
    # SummedInt
    2097152,
    # SmallInt
    65535,
    32767,
]
