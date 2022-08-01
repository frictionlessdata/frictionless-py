# type: ignore
from __future__ import annotations
from ...pipeline import Step
from ...resource import Resource


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

    metadata_profile_patch = {
        "required": ["path"],
        "properties": {
            "path": {"type": "string"},
        },
    }
