from __future__ import annotations
import attrs
from typing import List
from ...pipeline import Pipeline, Step
from ...exception import FrictionlessException
from ... import errors


@attrs.define(kw_only=True)
class resource_transform(Step):
    """Transform resource"""

    type = "resource-transform"

    # State

    name: str
    """NOTE: add docs"""

    steps: List[Step]
    """NOTE: add docs"""

    # Transform

    def transform_package(self, package):
        resource = package.get_resource(self.name)
        index = package.resources.index(resource)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{self.name}"')
            raise FrictionlessException(error=error)
        package.resources[index] = resource.transform(Pipeline(steps=self.steps))  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["name", "steps"],
        "properties": {
            "name": {"type": "string"},
            "steps": {"type": "array"},
        },
    }
