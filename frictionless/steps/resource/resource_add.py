from ...step import Step
from ...resource import Resource
from ... import helpers


# NOTE:
# Some of the following step use **options - we need to review/fix it
# The step updating resource might benefit from having schema_patch argument


class resource_add(Step):
    """Add resource"""

    code = "resource-add"

    def __init__(
        self,
        *,
        name: str,
        **options,
    ):
        self.name = name
        self.descriptor = helpers.create_descriptor(**options)

    # Properties

    name: str
    """TODO: add docs"""

    descriptor: dict
    """TODO: add docs"""

    # Transform

    def transform_package(self, package):
        descriptor = self.descriptor.copy()
        resource = Resource(descriptor, basepath=package.basepath)
        resource.infer()
        package.add_resource(resource)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name"],
        "properties": {
            "code": {},
            "name": {"type": "string"},
        },
    }
