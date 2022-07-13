# type: ignore
from __future__ import annotations
import attrs
from typing import List
from ...pipeline import Step
from ...schema import Field


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Some of the following step use **options - we need to review/fix it


@attrs.define(kw_only=True)
class field_unpack(Step):
    """Unpack field"""

    type = "field-unpack"

    # State

    name: str
    """TODO: add docs"""

    to_names: List[str]
    """TODO: add docs"""

    preserve: bool = False
    """TODO: add docs"""

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
