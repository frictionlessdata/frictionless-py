# type: ignore
from __future__ import annotations
from ...pipeline import Step
from ...platform import platform
from ...resource import Resource


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
        function = (
            platform.petl.hashintersection if use_hash else platform.petl.intersection
        )
        resource.data = function(view1, view2)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["resource"],
        "properties": {
            "resource": {},
            "useHash": {},
        },
    }
