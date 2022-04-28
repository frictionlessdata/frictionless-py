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


class table_melt(Step):
    """Melt tables"""

    code = "table-melt"

    def __init__(
        self,
        descriptor=None,
        *,
        variables=None,
        field_name=None,
        to_field_names=None,
    ):
        self.setinitial("variables", variables)
        self.setinitial("fieldName", field_name)
        self.setinitial("toFieldNames", to_field_names)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        variables = self.get("variables")
        field_name = self.get("fieldName")
        to_field_names = self.get("toFieldNames", ["variable", "value"])
        field = resource.schema.get_field(field_name)
        resource.schema.fields.clear()
        resource.schema.add_field(field)
        for name in to_field_names:
            resource.schema.add_field(Field(name=name))
        resource.data = table.melt(
            key=field_name,
            variables=variables,
            variablefield=to_field_names[0],
            valuefield=to_field_names[1],
        )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["fieldName"],
        "properties": {
            "fieldName": {"type": "string"},
            "variables": {"type": "array"},
            "toFieldNames": {"type": "array", "minItems": 2, "maxItems": 2},
        },
    }
