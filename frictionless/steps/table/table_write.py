from ...step import Step
from ...resource import Resource


# NOTE:
# We might consider implementing table_preload/cache step
# Some of the following step use **options - we need to review/fix it
# Currently, metadata profiles are not fully finished; will require improvements
# We need to review table_pivot step as it's not fully implemented/tested
# We need to review table_validate step as it's not fully implemented/tested
# We need to review table_write step as it's not fully implemented/tested
# We need to review how we use "target.schema.fields.clear()"


class table_write(Step):
    """Write table"""

    code = "table-write"

    def __init__(self, descriptor=None, *, path=None, **options):
        self.setinitial("path", path)
        self.setinitial("options", options)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        path = self.get("path")
        options = self.get("options")
        resource.write(Resource(path=path, **options))

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["path"],
        "properties": {
            "path": {"type": "string"},
        },
    }
