from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import attrs

from ...pipeline import Step
from ...platform import platform

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class row_ungroup(Step):
    """Ungroup rows.

    This step can be added using the `steps` parameter
    for the `transform` function.
    """

    type = "row-ungroup"

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

    def transform_resource(self, resource: Resource):
        table = resource.to_petl()  # type: ignore
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
