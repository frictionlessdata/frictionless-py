from __future__ import annotations
import attrs
from typing import Any
from ...pipeline import Step


@attrs.define(kw_only=True)
class cell_set(Step):
    """Set cell"""

    type = "cell-set"

    # State

    value: Any
    """
    Value to be set in cell of the given field.
    """

    field_name: str
    """
    Specifies the field name where to set/replace the value.
    """

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        resource.data = table.update(self.field_name, self.value)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "fieldName": {"type": "string"},
            "value": {},
        },
    }
