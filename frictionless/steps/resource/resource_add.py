from __future__ import annotations
from ...pipeline import Step
from ...resource import Resource
from ... import helpers


# TODO: migrate to dataclass
class resource_add(Step):
    """Add resource"""

    type = "resource-add"

    def __init__(
        self,
        *,
        name: str,
        **options,
    ):
        self.name = name
        self.descriptor = helpers.create_descriptor(**options)

    # State

    name: str
    """NOTE: add docs"""

    descriptor: dict
    """NOTE: add docs"""

    # Transform

    def transform_package(self, package):
        descriptor = self.descriptor.copy()
        resource = Resource(descriptor, basepath=package.basepath)
        resource.infer()
        package.add_resource(resource)

    # Metadata

    metadata_profile_patch = {
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
        },
    }
