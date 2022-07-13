from __future__ import annotations
import attrs
import hashlib
from ...checklist import Check
from ... import errors


@attrs.define(kw_only=True)
class duplicate_row(Check):
    """Check for duplicate rows

    This check can be enabled using the `checks` parameter
    for the `validate` function.

    """

    type = "duplicate-row"
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
        self.__memory[hash] = row.row_number
