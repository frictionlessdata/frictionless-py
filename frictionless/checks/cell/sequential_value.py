from __future__ import annotations
import attrs
from ...checklist import Check
from ... import errors


@attrs.define(kw_only=True)
class sequential_value(Check):
    """Check that a column having sequential values."""

    type = "sequential-value"
    Errors = [errors.SequentialValueError]

    # State

    field_name: str
    """
    The name of the field to apply the check. Check will not be 
    applied to other fields.
    """

    # Connect

    def connect(self, resource):
        super().connect(resource)
        self.__cursor = None
        self.__exited = False

    # Validate

    def validate_start(self):
        if self.field_name not in self.resource.schema.field_names:  # type: ignore
            note = 'sequential value check requires field "%s"' % self.field_name
            yield errors.CheckError(note=note)

    def validate_row(self, row):
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
