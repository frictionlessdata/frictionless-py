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
    """Add field.

    This step can be added using the `steps` parameter
    for the `transform` function.
    """

    type = "field-add"

    # State

    name: str
    """
    A human-oriented name for the field.
    """

    value: Optional[Any] = None
    """
    Specifies value for the field.
    """

    formula: Optional[Any] = None
    """
    Evaluatable expressions to set the value for the field. The expressions are 
    processed using simpleeval library.
    """

    function: Optional[Any] = None
    """
    Python function to set the value for the field.
    """

    position: Optional[int] = None
    """
    Position index where to add the field. For example, to 
    add the field in second position, we need to set it as 'position=2'.
    """

    descriptor: Optional[IDescriptor] = None
    """
    A dictionary, which contains metadata for the field which
    describes the properties of the field.
    """

    incremental: bool = False
    """
    Indicates if it is an incremental value. If True, the sequential value is set
    to the new field. The default value is false.
    """

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
