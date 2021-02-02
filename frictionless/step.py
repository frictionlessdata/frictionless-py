from .metadata import Metadata
from . import errors


# NOTE:
# We might consider migrating transform_resource API to emitting
# data as an ouput instead of setting it to target.data
# It might make custom transform steps more eloquent
# This change probably not even breaking because it will be a new
# mode supported by the system (function emiting data instead of returning None)


class Step(Metadata):
    code = "step"

    def __init__(self, descriptor=None, *, function=None):
        super().__init__(descriptor)
        self.setinitial("code", self.code)
        self.__function = function

    # Transform

    def transform_resource(self, source, target):
        if self.__function:
            self.__function(source, target)

    def transform_package(self, source, target):
        if self.__function:
            self.__function(source, target)

    # Metadata

    metadata_strict = True
    metadata_Error = errors.StepError
