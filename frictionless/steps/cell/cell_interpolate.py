from __future__ import annotations
import attrs
from typing import Optional
from ...pipeline import Step


@attrs.define(kw_only=True)
class cell_interpolate(Step):
    """Interpolate cell

    Interpolate all values in a given or all string fields using the `template` string.

    """

    type = "cell-interpolate"

    template: str
    """template string to apply to the field cells"""

    field_name: Optional[str] = None
    """field name to apply template string"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        if not self.field_name:
            resource.data = table.interpolateall(self.template)  # type: ignore
        else:
            resource.data = table.interpolate(self.field_name, self.template)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["template"],
        "properties": {
            "template": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }
