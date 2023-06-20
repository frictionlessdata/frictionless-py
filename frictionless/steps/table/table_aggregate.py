from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

import attrs

from ... import fields
from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class table_aggregate(Step):
    """Aggregate table.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-aggregate"

    aggregation: Dict[str, Any]
    """
    A dictionary with aggregation function. The values
    could be max, min, len and sum.
    """

    group_name: str
    """
    Field by which the rows will be grouped.
    """

    # Transform

    def transform_resource(self, resource: Resource):
        table = resource.to_petl()  # type: ignore
        field = resource.schema.get_field(self.group_name)
        resource.schema.fields.clear()
        resource.schema.add_field(field)
        for name in self.aggregation.keys():
            resource.schema.add_field(fields.AnyField(name=name))
        resource.data = table.aggregate(self.group_name, self.aggregation)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "type": "object",
        "required": ["groupName", "aggregation"],
        "properties": {
            "groupName": {"type": "string"},
            "aggregation": {"type": "object"},
        },
    }
