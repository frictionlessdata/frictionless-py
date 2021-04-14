from ..step import Step
from ..resource import Resource
from ..transform import transform_resource
from ..exception import FrictionlessException
from .. import helpers
from .. import errors


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


class resource_update(Step):
    """Update resource"""

    code = "resource-update"

    def __init__(self, descriptor=None, *, name=None, **options):
        self.setinitial("name", name)
        for key, value in helpers.create_descriptor(**options).items():
            self.setinitial(key, value)
        super().__init__(descriptor)

    # Transform

    def transform_package(self, package):
        descriptor = self.to_dict()
        descriptor.pop("code", None)
        name = descriptor.pop("name", None)
        resource = package.get_resource(name)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{name}"')
            raise FrictionlessException(error=error)
        resource.update(descriptor)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
        },
    }
