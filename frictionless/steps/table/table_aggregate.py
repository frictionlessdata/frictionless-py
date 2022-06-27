from dataclasses import dataclass
from ...step import Step
from ...schema import Field


# NOTE:
# We might consider implementing table_preload/cache step
# Some of the following step use **options - we need to review/fix it
# Currently, metadata profiles are not fully finished; will require improvements
# We need to review table_pivot step as it's not fully implemented/tested
# We need to review table_validate step as it's not fully implemented/tested
# We need to review table_write step as it's not fully implemented/tested
# We need to review how we use "target.schema.fields.clear()"


@dataclass
class table_aggregate(Step):
    """Aggregate table"""

    code = "table-aggregate"

    # Properties

    aggregation: str
    """TODO: add docs"""

    group_name: str
    """TODO: add docs"""

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

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["groupName", "aggregation"],
        "properties": {
            "code": {},
            "groupName": {"type": "string"},
            "aggregation": {},
        },
    }
