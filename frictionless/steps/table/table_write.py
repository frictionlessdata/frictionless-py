# type: ignore
from __future__ import annotations
from ...pipeline import Step
from ...resource import Resource


# NOTE:
# We might consider implementing table_preload/cache step
# Some of the following step use **options - we need to review/fix it
# Currently, metadata profiles are not fully finished; will require improvements
# We need to review table_pivot step as it's not fully implemented/tested
# We need to review table_validate step as it's not fully implemented/tested
# We need to review table_write step as it's not fully implemented/tested
# We need to review how we use "target.schema.fields.clear()"


# TODO: migrate
class table_write(Step):
    """Write table"""

    type = "table-write"

    def __init__(self, descriptor=None, *, path=None, **options):
        self.setinitial("path", path)
        self.setinitial("options", options)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        path = self.get("path")
        options = self.get("options")
        resource.write(Resource(path=path, **options))  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["path"],
        "properties": {
            "type": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "path": {"type": "string"},
        },
    }
