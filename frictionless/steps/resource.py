from ..step import Step
from ..resource import Resource
from .. import exceptions
from .. import errors


class resource_add(Step):
    def __init__(self, *, name, **options):
        self.__name = name
        self.__options = options

    def transform_package(self, source, target):
        # TODO: review whether package.add_resource can handle basepath/etc?
        resource = Resource(name=self.__name, **self.__options, basepath=target.basepath)
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


class resource_update(Step):
    def __init__(self, *, name, **options):
        self.__name = name
        self.__options = options

    def transform_package(self, source, target):
        # TODO: this method should raise instead of returning None?
        resource = target.get_resource(self.__name)
        if not resource:
            error = errors.ResourceError(note=f'No resource "{self.__name}"')
            raise exceptions.FrictionlessException(error=error)
        for name, value in self.__options.items():
            setattr(resource, name, value)
