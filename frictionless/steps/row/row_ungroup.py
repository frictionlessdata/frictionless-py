from __future__ import annotations
import attrs
import petl
from typing import Optional
from ...pipeline import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


@attrs.define(kw_only=True)
class row_ungroup(Step):
    """Ungroup rows"""

    type = "row-ungroup"

    # State

    selection: str
    """TODO: add docs"""

    group_name: str
    """TODO: add docs"""

    value_name: Optional[str] = None
    """TODO: add docs"""

    def transform_resource(self, resource):
        table = resource.to_petl()
        function = getattr(petl, f"groupselect{self.selection}")
        if self.selection in ["first", "last"]:
            resource.data = function(table, self.group_name)
        else:
            resource.data = function(table, self.group_name, self.value_name)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["groupName", "selection"],
        "properties": {
            "type": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "selection": {
                "type": "string",
                "enum": ["first", "last", "min", "max"],
            },
            "groupName": {"type": "string"},
            "valueName": {"type": "string"},
        },
    }
