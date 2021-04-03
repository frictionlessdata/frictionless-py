from ..step import Step
from ..resource import Resource
from ..transform import transform_resource
from ..exception import FrictionlessException
from .. import errors


# NOTE:
# Some of the following step use **options - we need to review/fix it
# The step updating resource might benefit from having schema_patch argument


class resource_add(Step):
    """Add resource"""

    code = "resource-add"

    def __init__(self, descriptor=None, *, name=None, **options):
        self.setinitial("name", name)
        self.setinitial("options", options)
        super().__init__(descriptor)
        self.__options = options

    # Transform

    def transform_package(self, package):
        name = self.get("name")
        options = self.get("options")
        resource = Resource(name=name, basepath=package.basepath, **options)
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
        self.setinitial("options", options)
        super().__init__(descriptor)

    # Transform

    def transform_package(self, package):
        name = self.get("name")
        options = self.get("options")
        resource = package.get_resource(name)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{name}"')
            raise FrictionlessException(error=error)
        for name, value in options.items():
            setattr(resource, name, value)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
        },
    }
