from __future__ import annotations
import attrs
from typing import Optional
from ...platform import platform
from ...pipeline import Step


@attrs.define(kw_only=True)
class row_ungroup(Step):
    """Ungroup rows"""

    type = "row-ungroup"

    # State

    selection: str
    """NOTE: add docs"""

    group_name: str
    """NOTE: add docs"""

    value_name: Optional[str] = None
    """NOTE: add docs"""

    def transform_resource(self, resource):
        table = resource.to_petl()
        function = getattr(platform.petl, f"groupselect{self.selection}")
        if self.selection in ["first", "last"]:
            resource.data = function(table, self.group_name)
        else:
            resource.data = function(table, self.group_name, self.value_name)

    # Metadata

    metadata_profile_patch = {
        "required": ["groupName", "selection"],
        "properties": {
            "selection": {
                "type": "string",
                "enum": ["first", "last", "min", "max"],
            },
            "groupName": {"type": "string"},
            "valueName": {"type": "string"},
        },
    }
