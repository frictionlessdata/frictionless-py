from __future__ import annotations

from typing import TYPE_CHECKING, Any

import attrs

from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class cell_set(Step):
    """Set cell"""

    type = "cell-set"

    value: Any
    """
    Value to be set in cell of the given field.
    """

    field_name: str
    """
    Specifies the field name where to set/replace the value.
    """

    # Transform

    def transform_resource(self, resource: Resource):
        table = resource.to_petl()  # type: ignore
        resource.data = table.update(self.field_name, self.value)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "fieldName": {"type": "string"},
            "value": {},
        },
    }
