from dataclasses import dataclass
from ...pipeline import Step
from ...exception import FrictionlessException
from ... import errors


# NOTE:
# Some of the following step use **options - we need to review/fix it
# The step updating resource might benefit from having schema_patch argument


@dataclass
class resource_remove(Step):
    """Remove resource"""

    type = "resource-remove"

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
            "type": {},
            "name": {"type": "string"},
        },
    }
