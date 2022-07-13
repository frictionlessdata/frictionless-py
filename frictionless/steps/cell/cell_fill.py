from __future__ import annotations
import attrs
from typing import Optional, Any
from ...pipeline import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


@attrs.define(kw_only=True)
class cell_fill(Step):
    """Fill cell"""

    type = "cell-fill"

    # State

    value: Optional[Any] = None
    """TODO: add docs"""

    field_name: Optional[str] = None
    """TODO: add docs"""

    direction: Optional[str] = None
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        if self.value:
            resource.data = table.convert(self.field_name, {None: self.value})  # type: ignore
        elif self.direction == "down":
            if self.field_name:
                resource.data = table.filldown(self.field_name)  # type: ignore
            else:
                resource.data = table.filldown()  # type: ignore
        elif self.direction == "right":
            resource.data = table.fillright()  # type: ignore
        elif self.direction == "left":
            resource.data = table.fillleft()  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "value": {},
            "fieldName": {"type": "string"},
            "direction": {
                "type": "string",
                "enum": ["down", "right", "left"],
            },
        },
    }
