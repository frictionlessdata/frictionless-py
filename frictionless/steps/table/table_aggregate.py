from ...step import Step
from ...field import Field


# NOTE:
# We might consider implementing table_preload/cache step
# Some of the following step use **options - we need to review/fix it
# Currently, metadata profiles are not fully finished; will require improvements
# We need to review table_pivot step as it's not fully implemented/tested
# We need to review table_validate step as it's not fully implemented/tested
# We need to review table_write step as it's not fully implemented/tested
# We need to review how we use "target.schema.fields.clear()"


class table_aggregate(Step):
    """Aggregate table"""

    code = "table-aggregate"

    def __init__(self, descriptor=None, *, group_name=None, aggregation=None):
        self.setinitial("groupName", group_name)
        self.setinitial("aggregation", aggregation)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        group_name = self.get("groupName")
        aggregation = self.get("aggregation")
        field = resource.schema.get_field(group_name)
        resource.schema.fields.clear()
        resource.schema.add_field(field)
        for name in aggregation.keys():
            resource.schema.add_field(Field(name=name))
        resource.data = table.aggregate(group_name, aggregation)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["groupName", "aggregation"],
        "properties": {
            "groupName": {"type": "string"},
            "aggregation": {},
        },
    }
