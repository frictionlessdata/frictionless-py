# type: ignore
from __future__ import annotations
import simpleeval
from typing import Optional, Any
from ...pipeline import Step
from ...schema import Field
from ... import helpers


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


# TODO: rebase on dataclass?
# TODO: proper support for options/descriptor/extra
class field_add(Step):
    """Add field"""

    type = "field-add"

    def __init__(
        self,
        *,
        name: str,
        value: Optional[Any] = None,
        formula: Optional[Any] = None,
        function: Optional[Any] = None,
        field_name: Optional[str] = None,
        position: Optional[int] = None,
        incremental: bool = False,
        **options,
    ):
        self.name = name
        self.value = value
        self.formula = formula
        self.function = function
        self.field_name = field_name
        self.position = position
        self.incremental = incremental
        self.descriptor = helpers.create_descriptor(**options)

    # State

    name: str
    """NOTE: add docs"""

    value: Optional[Any]
    """NOTE: add docs"""

    formula: Optional[Any]
    """NOTE: add docs"""

    function: Optional[Any]
    """NOTE: add docs"""

    field_name: Optional[str]
    """NOTE: add docs"""

    position: Optional[int]
    """NOTE: add docs"""

    incremental: bool
    """NOTE: add docs"""

    descriptor: dict
    """NOTE: add docs"""

    # Transform

    def transform_resource(self, resource):
        value = self.value
        function = self.function
        table = resource.to_petl()
        field = Field(self.descriptor, name=self.name)
        index = self.position - 1 if self.position else None
        if index is None:
            resource.schema.add_field(field)
        else:
            resource.schema.fields.insert(index, field)
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
            "formula": {},
            "fieldName": {},
            "position": {},
            "incremental": {},
        },
    }
