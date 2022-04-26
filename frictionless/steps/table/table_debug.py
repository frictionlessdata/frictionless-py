from ...step import Step


# NOTE:
# We might consider implementing table_preload/cache step
# Some of the following step use **options - we need to review/fix it
# Currently, metadata profiles are not fully finished; will require improvements
# We need to review table_pivot step as it's not fully implemented/tested
# We need to review table_validate step as it's not fully implemented/tested
# We need to review table_write step as it's not fully implemented/tested
# We need to review how we use "target.schema.fields.clear()"


class table_debug(Step):
    """Debug table"""

    code = "table-debug"

    def __init__(self, descriptor=None, *, function=None):
        self.setinitial("function", function)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        current = resource.to_copy()
        function = self.get("function")

        # Data
        def data():
            with current:
                for row in current.row_stream:
                    function(row)
                    yield row

        # Meta
        resource.data = data

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["function"],
        "properties": {
            "function": {},
        },
    }
