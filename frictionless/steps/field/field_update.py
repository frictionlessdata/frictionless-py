from __future__ import annotations
import attrs
import simpleeval
from copy import deepcopy
from typing import TYPE_CHECKING, Optional, Any
from ...pipeline import Step

if TYPE_CHECKING:
    from ...interfaces import IDescriptor


@attrs.define(kw_only=True)
class field_update(Step):
    """Update field.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "field-update"

    # State

    name: str
    """
    Name of the field to update.
    """

    value: Optional[Any] = None
    """
    Cell value to set for the field.
    """

    formula: Optional[Any] = None
    """
    Evaluatable expressions to set the value for the field. The expressions 
    are processed using simpleeval library.
    """

    function: Optional[Any] = None
    """
    Python function to set the value for the field.
    """

    descriptor: Optional[IDescriptor] = None
    """
    A descriptor for the field to set the metadata.
    """

    # Transform

    def transform_resource(self, resource):
        function = self.function
        pass_row = False
        table = resource.to_petl()
        descriptor = deepcopy(self.descriptor) or {}
        new_name = descriptor.get("name")
        resource.schema.update_field(self.name, descriptor)
        if self.formula:
            function = lambda _, row: simpleeval.simple_eval(self.formula, names=row)
            pass_row = True
        if function:
            resource.data = table.convert(self.name, function, pass_row=pass_row)  # type: ignore
        elif self.value:
            resource.data = table.update(self.name, self.value)  # type: ignore
        elif new_name:
            resource.data = table.rename({self.name: new_name})  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "value": {},
            "formula": {"type": "string"},
            "descriptor": {"type": "object"},
        },
    }
