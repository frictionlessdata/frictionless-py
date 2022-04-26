from ...step import Step
from ...exception import FrictionlessException
from ... import errors


# NOTE:
# Some of the following step use **options - we need to review/fix it
# The step updating resource might benefit from having schema_patch argument


class resource_remove(Step):
    """Remove resource"""

    code = "resource-remove"

    def __init__(self, descriptor=None, *, name=None):
        self.setinitial("name", name)
        super().__init__(descriptor)

    # Transform

    def transform_package(self, package):
        name = self.get("name")
        resource = package.get_resource(name)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{name}"')
            raise FrictionlessException(error=error)
        package.remove_resource(name)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
        },
    }
