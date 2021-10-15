from .metadata import Metadata
from . import errors


# NOTE:
# We might consider migrating transform_resource API to emitting
# data as an ouput instead of setting it to target.data
# It might make custom transform steps more eloquent
# This change probably not even breaking because it will be a new
# mode supported by the system (function emiting data instead of returning None)
# We might consider adding `process_schema/row` etc to the Step class


class Step(Metadata):
    """Step representation"""

    code = "step"

    def __init__(self, descriptor=None, *, function=None):
        super().__init__(descriptor)
        self.setinitial("code", self.code)
        self.__function = function

    # Transform

    def transform_resource(self, resource):
        """Transform resource

        Parameters:
            resource (Resource): resource

        Returns:
            resource (Resource): resource
        """
        if self.__function:
            return self.__function(resource)

    def transform_package(self, resource):
        """Transform package

        Parameters:
            package (Package): package

        Returns:
            package (Package): package
        """
        if self.__function:
            return self.__function(resource)

    # Metadata

    metadata_Error = errors.StepError
