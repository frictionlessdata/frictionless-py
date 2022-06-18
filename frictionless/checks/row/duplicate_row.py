import hashlib
from ... import errors
from ...check import Check


class duplicate_row(Check):
    """Check for duplicate rows

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(checks=[{"code": "duplicate-row"}])`

    This check can be enabled using the `checks` parameter
    for the `validate` function.

    """

    code = "duplicate-row"
    Errors = [errors.DuplicateRowError]

    # Connect

    def connect(self, resource):
        super().connect(resource)
        self.__memory = {}

    # Validate

    def validate_row(self, row):
        text = ",".join(map(str, row.values()))
        hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        match = self.__memory.get(hash)
        if match:
            note = 'the same as row at position "%s"' % match
            yield errors.DuplicateRowError.from_row(row, note=note)
        self.__memory[hash] = row.row_position

    # Metadata

    metadata_profile = {
        "type": "object",
        "properties": {
            "code": {},
        },
    }
