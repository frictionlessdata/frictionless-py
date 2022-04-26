from ...step import Step
from ... import helpers


# NOTE:
# Some of the following step use **options - we need to review/fix it
# The step updating resource might benefit from having schema_patch argument


class resource_update(Step):
    """Update resource"""

    code = "resource-update"

    def __init__(self, descriptor=None, *, name=None, new_name=None, **options):
        self.setinitial("name", name)
        self.setinitial("newName", new_name)
        for key, value in helpers.create_descriptor(**options).items():
            self.setinitial(key, value)
        super().__init__(descriptor)

    # Transform

    def transform_package(self, package):
        descriptor = self.to_dict()
        descriptor.pop("code", None)
        name = descriptor.pop("name", None)
        new_name = descriptor.pop("newName", None)
        if new_name:
            descriptor["name"] = new_name
        resource = package.get_resource(name)
        resource.update(descriptor)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "newName": {"type": "string"},
        },
    }
