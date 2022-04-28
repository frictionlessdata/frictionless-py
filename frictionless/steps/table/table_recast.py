from ...step import Step


# NOTE:
# We might consider implementing table_preload/cache step
# Some of the following step use **options - we need to review/fix it
# Currently, metadata profiles are not fully finished; will require improvements
# We need to review table_pivot step as it's not fully implemented/tested
# We need to review table_validate step as it's not fully implemented/tested
# We need to review table_write step as it's not fully implemented/tested
# We need to review how we use "target.schema.fields.clear()"


class table_recast(Step):
    """Recast table"""

    code = "table-recast"

    def __init__(
        self,
        descriptor=None,
        *,
        field_name,
        from_field_names=None,
    ):
        self.setinitial("fieldName", field_name)
        self.setinitial("fromFieldNames", from_field_names)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        field_name = self.get("fieldName")
        from_field_names = self.get("fromFieldNames", ["variable", "value"])
        resource.pop("schema", None)
        resource.data = table.recast(
            key=field_name,
            variablefield=from_field_names[0],
            valuefield=from_field_names[1],
        )
        resource.infer()

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["fieldName"],
        "properties": {
            "fieldName": {"type": "string"},
            "fromFieldNames": {"type": "array", "minItems": 2, "maxItems": 2},
        },
    }
