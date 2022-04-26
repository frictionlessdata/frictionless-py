from ...step import Step


# NOTE:
# We might consider implementing table_preload/cache step
# Some of the following step use **options - we need to review/fix it
# Currently, metadata profiles are not fully finished; will require improvements
# We need to review table_pivot step as it's not fully implemented/tested
# We need to review table_validate step as it's not fully implemented/tested
# We need to review table_write step as it's not fully implemented/tested
# We need to review how we use "target.schema.fields.clear()"


class table_pivot(Step):
    """Pivot table"""

    code = "table-pivot"

    def __init__(self, descriptor=None, **options):
        self.setinitial("options", options)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        options = self.get("options")
        resource.pop("schema", None)
        resource.data = table.pivot(**options)
        resource.infer()

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {},
    }
