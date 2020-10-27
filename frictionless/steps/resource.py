from ..step import Step
from .. import exceptions
from .. import errors


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
