from __future__ import annotations
import attrs
from typing import List
from ...pipeline import Pipeline, Step
from ...exception import FrictionlessException
from ... import errors


# NOTE:
# Some of the following step use **options - we need to review/fix it
# The step updating resource might benefit from having schema_patch argument


@attrs.define(kw_only=True)
class resource_transform(Step):
    """Transform resource"""

    type = "resource-transform"

    # State

    name: str
    """TODO: add docs"""

    steps: List[Step]
    """TODO: add docs"""

    # Transform

    def transform_package(self, package):
        resource = package.get_resource(self.name)
        index = package.resources.index(resource)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{self.name}"')
            raise FrictionlessException(error=error)
        package.resources[index] = resource.transform(Pipeline(steps=self.steps))  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name", "steps"],
        "properties": {
            "type": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "name": {"type": "string"},
            "steps": {"type": "array"},
        },
    }
