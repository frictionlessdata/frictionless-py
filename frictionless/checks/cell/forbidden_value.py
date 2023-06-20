from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, List

import attrs

from ... import errors
from ...checklist import Check

if TYPE_CHECKING:
    from ...error import Error
    from ...table import Row


@attrs.define(kw_only=True, repr=False)
class forbidden_value(Check):
    """Check for forbidden values in a field."""

    type = "forbidden-value"
    Errors = [errors.ForbiddenValueError]

    field_name: str
    """
    The name of the field to apply the check. Check will not be applied to
    other fields.
    """

    values: List[Any]
    """
    Specify the forbidden values to check for, in the field specified by
    "field_name".
    """

    # Validate

    def validate_start(self) -> Iterable[Error]:
        if self.field_name not in self.resource.schema.field_names:  # type: ignore
            note = 'forbidden value check requires field "%s"' % self.field_name
            yield errors.CheckError(note=note)

    def validate_row(self, row: Row):
        cell = row[self.field_name]
        if cell in self.values:
            yield errors.ForbiddenValueError.from_row(
                row,
                note='forbidden values are "%s"' % self.values,
                field_name=self.field_name,
            )

    # Metadata

    metadata_profile_patch = {
        "required": ["fieldName", "values"],
        "properties": {
            "fieldName": {"type": "string"},
            "values": {"type": "array"},
        },
    }
