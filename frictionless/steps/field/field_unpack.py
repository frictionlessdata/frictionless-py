# type: ignore
from __future__ import annotations
import attrs
from typing import List
from ...pipeline import Step
from ...schema import Field


@attrs.define(kw_only=True)
class field_unpack(Step):
    """Unpack field"""

    type = "field-unpack"

    # State

    name: str
    """NOTE: add docs"""

    to_names: List[str]
    """NOTE: add docs"""

    preserve: bool = False
    """NOTE: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        field = resource.schema.get_field(self.name)
        for to_name in self.to_names:  # type: ignore
            resource.schema.add_field(Field(name=to_name))
        if not self.preserve:
            resource.schema.remove_field(self.name)
        if field.type == "object":
            processor = table.unpackdict  # type: ignore
            resource.data = processor(
                self.name, self.to_names, includeoriginal=self.preserve
            )
        else:
            processor = table.unpack  # type: ignore
            resource.data = processor(
                self.name, self.to_names, include_original=self.preserve
            )

    # Metadata

    metadata_profile_patch = {
        "required": ["name", "toNames"],
        "properties": {
            "name": {"type": "string"},
            "toNames": {"type": "array"},
            "preserve": {},
        },
    }
