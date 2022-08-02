from __future__ import annotations
import attrs
import simpleeval
from copy import deepcopy
from typing import TYPE_CHECKING, Optional, Any
from ...pipeline import Step
from ...schema import Field

if TYPE_CHECKING:
    from ...interfaces import IDescriptor


@attrs.define(kw_only=True)
class field_add(Step):
    """Add field"""

    type = "field-add"

    # State

    name: str
    """NOTE: add docs"""

    value: Optional[Any] = None
    """NOTE: add docs"""

    formula: Optional[Any] = None
    """NOTE: add docs"""

    function: Optional[Any] = None
    """NOTE: add docs"""

    position: Optional[int] = None
    """NOTE: add docs"""

    descriptor: Optional[IDescriptor] = None
    """NOTE: add docs"""

    incremental: bool = False
    """NOTE: add docs"""

    # Transform

    def transform_resource(self, resource):
        value = self.value
        position = self.position
        function = self.function
        table = resource.to_petl()
        descriptor = deepcopy(self.descriptor) or {}
        if self.name:
            descriptor["name"] = self.name
        descriptor.setdefault("type", "any")
        if self.incremental:
            position = position or 1
            descriptor["type"] = "integer"
        field = Field.from_descriptor(descriptor)
        index = position - 1 if position else None
        resource.schema.add_field(field, position=position)
        if self.incremental:
            resource.data = table.addrownumbers(field=self.name)  # type: ignore
        else:
            if self.formula:
                function = lambda row: simpleeval.simple_eval(self.formula, names=row)
            value = value or function
            resource.data = table.addfield(self.name, value=value, index=index)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "value": {},
            "formula": {"type": "string"},
            "position": {"type": "integer"},
            "descriptor": {"type": "object"},
            "incremental": {"type": "boolean"},
        },
    }
