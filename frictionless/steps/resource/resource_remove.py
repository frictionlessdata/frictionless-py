from __future__ import annotations
import attrs
from ...pipeline import Step
from ...exception import FrictionlessException
from ... import errors


@attrs.define(kw_only=True)
class resource_remove(Step):
    """Remove resource"""

    type = "resource-remove"

    # State

    name: str
    """NOTE: add docs"""

    # Transform

    def transform_package(self, package):
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
