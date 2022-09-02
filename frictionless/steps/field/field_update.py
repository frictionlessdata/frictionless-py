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
    """Update field"""

    type = "field-update"

    # State

    name: str
    """NOTE: add docs"""

    value: Optional[Any] = None
    """NOTE: add docs"""

    formula: Optional[Any] = None
    """NOTE: add docs"""

    function: Optional[Any] = None
    """NOTE: add docs"""

    descriptor: Optional[IDescriptor] = None
    """NOTE: add docs"""

    # Transform

    def transform_resource(self, resource):
        function = self.function
        table = resource.to_petl()
        descriptor = deepcopy(self.descriptor) or {}
        new_name = descriptor.get("name")
        resource.schema.update_field(self.name, descriptor)
        if self.formula:
            function = lambda _, row: simpleeval.simple_eval(self.formula, names=row)
        if function:
            resource.data = table.convert(self.name, function)  # type: ignore
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
