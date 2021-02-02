from ..step import Step
from ..resource import Resource
from ..transform import transform_resource
from ..exception import FrictionlessException
from .. import errors


# NOTE:
# Some of the following step use **options - we need to review/fix it
# The step updating resource might benefit from having schema_patch argument


class resource_add(Step):
    code = "resource-add"

    def __init__(self, descriptor=None, *, name=None, **options):
        self.setinitial("name", name)
        self.setinitial("options", options)
        super().__init__(descriptor)
        self.__options = options

    # Transform

    def transform_package(self, source, target):
        name = self.get("name")
        options = self.get("options")
        resource = Resource(name=name, basepath=target.basepath, **options)
        resource.infer()
        target.add_resource(resource)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
        },
    }


class resource_remove(Step):
    code = "resource-remove"

    def __init__(self, descriptor=None, *, name=None):
        self.setinitial("name", name)
        super().__init__(descriptor)

    # Transform

    def transform_package(self, source, target):
        name = self.get("name")
        resource = target.get_resource(name)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{name}"')
            raise FrictionlessException(error=error)
        target.remove_resource(name)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
        },
    }


class resource_transform(Step):
    code = "resource-transform"

    def __init__(self, descriptor=None, *, name=None, steps=None):
        self.setinitial("name", name)
        self.setinitial("steps", steps)
        super().__init__(descriptor)

    # Transform

    def transform_package(self, source, target):
        name = self.get("name")
        steps = self.get("steps")
        resource = target.get_resource(name)
        index = target.resources.index(resource)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{name}"')
            raise FrictionlessException(error=error)
        target.resources[index] = transform_resource(resource, steps=steps)

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
    code = "resource-update"

    def __init__(self, descriptor=None, *, name=None, **options):
        self.setinitial("name", name)
        self.setinitial("options", options)
        super().__init__(descriptor)

    # Transform

    def transform_package(self, source, target):
        name = self.get("name")
        options = self.get("options")
        resource = target.get_resource(name)
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
