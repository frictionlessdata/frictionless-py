from ...step import Step


# NOTE:
# We might consider implementing table_preload/cache step
# Some of the following step use **options - we need to review/fix it
# Currently, metadata profiles are not fully finished; will require improvements
# We need to review table_pivot step as it's not fully implemented/tested
# We need to review table_validate step as it's not fully implemented/tested
# We need to review table_write step as it's not fully implemented/tested
# We need to review how we use "target.schema.fields.clear()"


class table_transpose(Step):
    """Transpose table"""

    code = "table-transpose"

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        resource.pop("schema", None)
        resource.data = table.transpose()
        resource.infer()

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {},
    }
