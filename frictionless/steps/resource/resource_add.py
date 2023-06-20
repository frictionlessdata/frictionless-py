from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

import attrs

from ...pipeline import Step
from ...resource import Resource

if TYPE_CHECKING:
    from ...package import Package


@attrs.define(kw_only=True, repr=False)
class resource_add(Step):
    """Add resource.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "resource-add"

    name: str
    """
    Name of the resource to add.
    """

    descriptor: Dict[str, Any]
    """
    A descriptor for the resource.
    """

    # Transform

    def transform_package(self, package: Package):
        descriptor = self.descriptor.copy()
        descriptor["name"] = self.name
        resource = Resource.from_descriptor(descriptor, basepath=package.basepath)
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
