# type: ignore
from __future__ import annotations
import petl
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
class table_intersect(Step):
    """Intersect tables"""

    type = "table-intersect"

    def __init__(self, descriptor=None, *, resource=None, use_hash=False):
        self.setinitial("resource", resource)
        self.setinitial("useHash", use_hash)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        target = resource
        source = self.get("resource")
        use_hash = self.get("useHash")
        if isinstance(source, str):
            source = target.package.get_resource(source)
        elif isinstance(source, dict):
            source = Resource(source)
        source.infer()  # type: ignore
        view1 = target.to_petl()
        view2 = source.to_petl()  # type: ignore
        function = petl.hashintersection if use_hash else petl.intersection
        resource.data = function(view1, view2)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["resource"],
        "properties": {
            "type": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "resource": {},
            "useHash": {},
        },
    }
