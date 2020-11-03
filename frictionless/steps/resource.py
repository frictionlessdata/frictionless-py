from ..step import Step
from ..resource import Resource
from ..transform import transform_resource
from .. import exceptions
from .. import errors


class resource_add(Step):
    def __init__(self, *, name, **options):
        self.__name = name
        self.__options = options

    def transform_package(self, source, target):
        resource = Resource(name=self.__name, basepath=target.basepath, **self.__options)
        resource.infer(only_sample=True)
        target.add_resource(resource)


class resource_remove(Step):
    def __init__(self, *, name):
        self.__name = name

    def transform_package(self, source, target):
        # TODO: this method should raise instead of returning None?
        resource = target.get_resource(self.__name)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{self.__name}"')
            raise exceptions.FrictionlessException(error=error)
        # TODO: this method should raise instead of ignoring?
        target.remove_resource(self.__name)


class resource_transform(Step):
    def __init__(self, *, name, steps):
        self.__name = name
        self.__steps = steps

    def transform_package(self, source, target):
        # TODO: this method should raise instead of returning None?
        resource = target.get_resource(self.__name)
        index = target.resources.index(resource)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{self.__name}"')
            raise exceptions.FrictionlessException(error=error)
        target.resources[index] = transform_resource(resource, steps=self.__steps)


# TODO: add patch_schema param?
class resource_update(Step):
    def __init__(self, *, name, steps=None, **options):
        self.__name = name
        self.__steps = steps
        self.__options = options

    def transform_package(self, source, target):
        # TODO: this method should raise instead of returning None?
        resource = target.get_resource(self.__name)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{self.__name}"')
            raise exceptions.FrictionlessException(error=error)
        for name, value in self.__options.items():
            setattr(resource, name, value)
