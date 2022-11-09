from __future__ import annotations
import attrs
from ...pipeline import Step
from ...resource import Resource


@attrs.define(kw_only=True)
class resource_add(Step):
    """Add resource.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "resource-add"

    # State

    name: str
    """
    Name of the resource to add.
    """

    descriptor: dict
    """
    A descriptor for the resource.
    """

    # Transform

    def transform_package(self, package):
        descriptor = self.descriptor.copy()
        resource = Resource.from_descriptor(
            descriptor,
            name=self.name,
            basepath=package.basepath,
        )
        resource.infer()
        package.add_resource(resource)

    # Metadata

    metadata_profile_patch = {
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "descriptor": {"type": "object"},
        },
    }
