from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

import attrs

from ... import errors
from ...checklist import Check

if TYPE_CHECKING:
    from ...error import Error
    from ...resource import Resource
    from ...table import Row


@attrs.define(kw_only=True, repr=False)
class sequential_value(Check):
    """Check that a column having sequential values."""

    type = "sequential-value"
    Errors = [errors.SequentialValueError]

    field_name: str
    """
    The name of the field to apply the check. Check will not be
    applied to other fields.
    """

    # Connect

    def connect(self, resource: Resource):
        super().connect(resource)
        self.__cursor = None
        self.__exited = False

    # Validate

    def validate_start(self) -> Iterable[Error]:
        if self.field_name not in self.resource.schema.field_names:  # type: ignore
            note = 'sequential value check requires field "%s"' % self.field_name
            yield errors.CheckError(note=note)

    def validate_row(self, row: Row):
        if not self.__exited:
            cell = row[self.field_name]
            try:
                self.__cursor = self.__cursor or cell
                assert self.__cursor == cell
                self.__cursor += 1
            except Exception:
                self.__exited = True
                yield errors.SequentialValueError.from_row(
                    row,
                    note="the value is not sequential",
                    field_name=self.field_name,
                )

    # Metadata

    metadata_profile_patch = {
        "required": ["fieldName"],
        "properties": {
            "fieldName": {"type": "string"},
        },
    }
