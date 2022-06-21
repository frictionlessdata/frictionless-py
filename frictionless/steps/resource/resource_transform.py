from typing import List
from dataclasses import dataclass
from ...step import Step
from ...pipeline import Pipeline
from ...exception import FrictionlessException
from ... import errors


# NOTE:
# Some of the following step use **options - we need to review/fix it
# The step updating resource might benefit from having schema_patch argument


@dataclass
class resource_transform(Step):
    """Transform resource"""

    code = "resource-transform"

    # Properties

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
            "code": {},
            "name": {"type": "string"},
            "steps": {"type": "array"},
        },
    }
