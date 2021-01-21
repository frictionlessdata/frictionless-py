from ..step import Step
from ..resource import Resource
from ..transform import transform_resource
from ..exception import FrictionlessException
from .. import errors


class resource_add(Step):
    code = "resource-add"

    def __init__(self, descriptor=None, *, name=None, **options):
        self.setinitial("name", name)
        # TODO: handle options
        super().__init__(descriptor)
        # TODO: reimplement
        self.__name = name
        self.__options = options

    # Transform

    def transform_package(self, source, target):
        resource = Resource(name=self.__name, basepath=target.basepath, **self.__options)
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
        # TODO: reimplement
        self.__name = self.get("name")

    # Transform

    def transform_package(self, source, target):
        # TODO: this method should raise instead of returning None?
        resource = target.get_resource(self.__name)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{self.__name}"')
            raise FrictionlessException(error=error)
        # TODO: this method should raise instead of ignoring?
        target.remove_resource(self.__name)

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
        # TODO: reimplement
        self.__name = name
        self.__steps = steps

    # Transform

    def transform_package(self, source, target):
        resource = target.get_resource(self.__name)
        index = target.resources.index(resource)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{self.__name}"')
            raise FrictionlessException(error=error)
        target.resources[index] = transform_resource(resource, steps=self.__steps)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name", "steps"],
        "properties": {
            "name": {"type": "string"},
            "steps": {"type": "array"},
        },
    }


# TODO: add patch_schema param?
class resource_update(Step):
    code = "resource-update"

    def __init__(self, descriptor=None, *, name=None, **options):
        self.setinitial("name", name)
        # TODO: handle options
        super().__init__(descriptor)
        # TODO: reimplement
        self.__name = name
        self.__options = options

    # Transform

    def transform_package(self, source, target):
        resource = target.get_resource(self.__name)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{self.__name}"')
            raise FrictionlessException(error=error)
        for name, value in self.__options.items():
            setattr(resource, name, value)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
        },
    }
