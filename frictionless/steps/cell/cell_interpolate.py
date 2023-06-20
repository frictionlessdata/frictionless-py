from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import attrs

from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
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

    def transform_resource(self, resource: Resource):
        table = resource.to_petl()  # type: ignore
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
