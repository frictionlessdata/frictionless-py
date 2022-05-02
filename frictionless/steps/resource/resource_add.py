from ...step import Step
from ...resource import Resource
from ... import helpers


# NOTE:
# Some of the following step use **options - we need to review/fix it
# The step updating resource might benefit from having schema_patch argument


class resource_add(Step):
    """Add resource"""

    code = "resource-add"

    def __init__(self, descriptor=None, *, name=None, **options):
        self.setinitial("name", name)
        for key, value in helpers.create_descriptor(**options).items():
            self.setinitial(key, value)
        super().__init__(descriptor)
        self.__options = options

    # Transform

    def transform_package(self, package):
        descriptor = self.to_dict()
        descriptor.pop("code", None)
        resource = Resource(descriptor, basepath=package.basepath)
        resource.infer()
        package.add_resource(resource)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
        },
    }
