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
    """NOTE: add docs"""

    field_name: str
    """NOTE: add docs"""

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
