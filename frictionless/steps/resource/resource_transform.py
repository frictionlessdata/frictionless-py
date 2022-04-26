from ...step import Step
from ...transform import transform_resource
from ...exception import FrictionlessException
from ... import errors


# NOTE:
# Some of the following step use **options - we need to review/fix it
# The step updating resource might benefit from having schema_patch argument


class resource_transform(Step):
    """Transform resource"""

    code = "resource-transform"

    def __init__(self, descriptor=None, *, name=None, steps=None):
        self.setinitial("name", name)
        self.setinitial("steps", steps)
        super().__init__(descriptor)

    # Transform

    def transform_package(self, package):
        name = self.get("name")
        steps = self.get("steps")
        resource = package.get_resource(name)
        index = package.resources.index(resource)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{name}"')
            raise FrictionlessException(error=error)
        package.resources[index] = transform_resource(resource, steps=steps)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name", "steps"],
        "properties": {
            "name": {"type": "string"},
            "steps": {"type": "array"},
        },
    }
