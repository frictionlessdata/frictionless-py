from __future__ import annotations
import attrs
from typing import Optional
from ...platform import platform
from ...pipeline import Step


@attrs.define(kw_only=True)
class row_ungroup(Step):
    """Ungroup rows.

    This step can be added using the `steps` parameter
    for the `transform` function.
    """

    type = "row-ungroup"

    # State

    selection: str
    """
    Specifies whether to return first or last row. The value
    can be "first", "last", "min" and "max".
    """

    group_name: str
    """
    Field name which will be used to group the rows. And it returns the 
    first or last row with each group based on the 'selection'.
    """

    value_name: Optional[str] = None
    """
    If the selection is set to "min" or "max", the rows will be grouped by 
    "group_name" field and min or max value will be then selected from the 
    "value_name" field.
    """

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
