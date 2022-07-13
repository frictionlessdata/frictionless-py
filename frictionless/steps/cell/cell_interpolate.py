from __future__ import annotations
import attrs
from typing import Optional
from ...pipeline import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


@attrs.define(kw_only=True)
class cell_interpolate(Step):
    """Interpolate cell"""

    type = "cell-interpolate"

    # State

    template: str
    """TODO: add docs"""

    field_name: Optional[str] = None
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        if not self.field_name:
            resource.data = table.interpolateall(self.template)  # type: ignore
        else:
            resource.data = table.interpolate(self.field_name, self.template)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["template"],
        "properties": {
            "type": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "template": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }
