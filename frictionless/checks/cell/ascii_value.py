from ... import errors
from ...check import Check
from typing import Union, Iterator


class ascii_value(Check):
    """Check for forbidden values in a field

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(checks=[{"code": "ascii-value"}])`

    This check can be enabled using the `checks` parameter
    for the `validate` function.

    Parameters:
       forbidden_values? (any[]): a list of forbidden values

    """

    code = "ascii-value"
    Errors = [errors.NotAscii]

    def __init__(
        self, descriptor: Union[list, None] = None, *, forbidden_values: list = []
    ):
        self.setinitial("ForbiddenValues", forbidden_values)
        super().__init__(descriptor)
        self.__forbidden_values = self.get("ForbiddenValues", [])

    # Validate

    def validate_row(self, row: any) -> Iterator[any]:
        for field_name, cell in row.items():
            not_ascii = False

            if cell is None:
                continue

            # Check if string is ascii
            if isinstance(cell, str):
                try:
                    cell.encode("ascii")
                except UnicodeEncodeError:
                    not_ascii = True

            # Check if string has forbidden ascii code
            if isinstance(cell, int):
                if cell in self.__forbidden_values:
                    yield errors.ForbiddenValueError.from_row(
                        row,
                        note='forbiddened values are "%s"' % self.__forbidden_values,
                        field_name=field_name,
                    )

            # Add error
            if not_ascii:
                note = "the value is not ascii"
                yield errors.NotAscii.from_row(row, note=note, field_name=field_name)

    # Metadata

    metadata_profile = {
        "type": "object",
        "required": ["ForbiddenValues"],
        "properties": {
            "ForbiddenValues": {"type": "array"},
        },
    }
