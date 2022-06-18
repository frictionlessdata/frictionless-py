from ...step import Step
from ...exception import FrictionlessException
from ... import errors


# NOTE:
# Some of the following step use **options - we need to review/fix it
# The step updating resource might benefit from having schema_patch argument


class resource_remove(Step):
    """Remove resource"""

    code = "resource-remove"

    def __init__(
        self,
        *,
        name: str,
    ):
        self.name = name

    # Properties

    name: str
    """TODO: add docs"""

    # Transform

    def transform_package(self, package):
        resource = package.get_resource(self.name)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{self.name}"')
            raise FrictionlessException(error=error)
        package.remove_resource(self.name)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name"],
        "properties": {
            "code": {},
            "name": {"type": "string"},
        },
    }
