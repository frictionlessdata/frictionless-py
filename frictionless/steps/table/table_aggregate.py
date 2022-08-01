# type: ignore
from __future__ import annotations
import attrs
from ...pipeline import Step
from ...schema import Field


@attrs.define(kw_only=True)
class table_aggregate(Step):
    """Aggregate table"""

    type = "table-aggregate"

    # State

    aggregation: str
    """NOTE: add docs"""

    group_name: str
    """NOTE: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        field = resource.schema.get_field(self.group_name)
        resource.schema.fields.clear()
        resource.schema.add_field(field)
        for name in self.aggregation.keys():  # type: ignore
            resource.schema.add_field(Field(name=name))
        resource.data = table.aggregate(self.group_name, self.aggregation)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "type": "object",
        "required": ["groupName", "aggregation"],
        "properties": {
            "groupName": {"type": "string"},
            "aggregation": {},
        },
    }
