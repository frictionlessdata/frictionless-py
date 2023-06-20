from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Dict

import attrs

from ... import errors
from ...checklist import Check

if TYPE_CHECKING:
    from ...resource import Resource
    from ...table import Row


@attrs.define(kw_only=True, repr=False)
class duplicate_row(Check):
    """Check for duplicate rows

    This check can be enabled using the `checks` parameter
    for the `validate` function.

    """

    type = "duplicate-row"
    Errors = [errors.DuplicateRowError]

    # Connect

    def connect(self, resource: Resource):
        super().connect(resource)
        self.__memory: Dict[str, int] = {}

    # Validate

    def validate_row(self, row: Row):
        text = ",".join(map(str, row.values()))
        hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        match = self.__memory.get(hash)
        if match:
            note = 'the same as row at position "%s"' % match
            yield errors.DuplicateRowError.from_row(row, note=note)
        self.__memory[hash] = row.row_number
