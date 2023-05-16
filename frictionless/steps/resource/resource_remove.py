from __future__ import annotations
import attrs
from typing import TYPE_CHECKING
from ...pipeline import Step
from ...exception import FrictionlessException
from ... import errors

if TYPE_CHECKING:
    from ...package import Package


@attrs.define(kw_only=True)
class resource_remove(Step):
    """Remove resource.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "resource-remove"

    name: str
    """
    Name of the resource to remove.
    """

    # Transform

    def transform_package(self, package: Package):
        resource = package.get_resource(self.name)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{self.name}"')
            raise FrictionlessException(error=error)
        package.remove_resource(self.name)

    # Metadata

    metadata_profile_patch = {
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
        },
    }
