from __future__ import annotations
import attrs
from typing import Any
from ...pipeline import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


@attrs.define(kw_only=True)
class cell_set(Step):
    """Set cell"""

    type = "cell-set"

    # State

    value: Any
    """TODO: add docs"""

    field_name: str
    """TODO: add docs"""

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
