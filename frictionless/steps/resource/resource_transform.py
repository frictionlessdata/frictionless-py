from __future__ import annotations
import attrs
from typing import List
from ...pipeline import Pipeline, Step
from ...exception import FrictionlessException
from ... import errors


@attrs.define(kw_only=True)
class resource_transform(Step):
    """Transform resource.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "resource-transform"

    # State

    name: str
    """
    Name of the resource to transform.
    """

    steps: List[Step]
    """
    List of transformation steps to apply to the given 
    resource.
    """

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
