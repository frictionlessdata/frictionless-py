from __future__ import annotations
import attrs
from copy import deepcopy
from typing import TYPE_CHECKING
from ...pipeline import Step

if TYPE_CHECKING:
    from ...interfaces import IDescriptor


@attrs.define(kw_only=True)
class resource_update(Step):
    """Update resource.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "resource-update"

    # State

    name: str
    """
    Name of the resource to update.
    """

    descriptor: IDescriptor
    """
    New descriptor for the resource to update metadata.
    """

    # Transform

    def transform_package(self, package):
        descriptor = deepcopy(self.descriptor)
        package.update_resource(self.name, descriptor)

    # Metadata

    metadata_profile_patch = {
        "required": ["name", "descriptor"],
        "properties": {
            "name": {"type": "string"},
            "descriptor": {"type": "object"},
        },
    }
