from __future__ import annotations
import attrs
from typing import TYPE_CHECKING, List, Any, Iterable
from ...checklist import Check
from ... import errors

if TYPE_CHECKING:
    from ...table import Row
    from ...error import Error
    from ...resource import Resource


@attrs.define(kw_only=True)
class required_value(Check):
    """Check for required values in a field."""

    type = "required-value"
    Errors = [errors.RequiredValueError]

    # State

    field_name: str
    """
    The name of the field to apply the check. Check will not be applied 
    to other fields.
    """

    values: List[Any]
    """
    List of required values that needs to be present in the field specified by "field_name". 
    The value should be present at least one or more times in the field.
    """

    # Connect

    def connect(self, resource: Resource):
        super().connect(resource)
        self.__required_values_in_cell = set()

    # Validate

    def validate_start(self) -> Iterable[Error]:
        if self.field_name not in self.resource.schema.field_names:  # type: ignore
            note = 'required value check requires field "%s" to exist'
            yield errors.CheckError(note=note % self.field_name)

    def validate_row(self, row: Row) -> Iterable[Error]:
        cell = row[self.field_name]
        if cell in self.values:
            self.__required_values_in_cell.add(cell)
        yield from []

    def validate_end(self) -> Iterable[Error]:
        required_values_not_found = set(self.values) - self.__required_values_in_cell
        if required_values_not_found:
            for missing_required_value in required_values_not_found:
                note = 'The value "%s" is required to be present in field "%s" in at least one row.'
                note = note % (missing_required_value, self.field_name)
                yield errors.RequiredValueError(note=note)

    # Metadata

    metadata_profile_patch = {
        "required": ["fieldName", "values"],
        "properties": {
            "fieldName": {"type": "string"},
            "values": {"type": "array"},
        },
    }
