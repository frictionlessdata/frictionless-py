from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

import attrs

from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class cell_fill(Step):
    """Fill cell

    Replaces missing values with non-missing values from the adjacent row/column.
    """

    type = "cell-fill"

    value: Optional[Any] = None
    """Value to replace in the field cell with missing value"""

    field_name: Optional[str] = None
    """Name of the field to replace the missing value cells"""

    direction: Optional[str] = None
    """Directions to read the non missing value from(left/right/above)"""

    # Transform

    def transform_resource(self, resource: Resource):
        table = resource.to_petl()  # type: ignore
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
