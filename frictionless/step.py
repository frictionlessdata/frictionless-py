from __future__ import annotations
from importlib import import_module
from typing import TYPE_CHECKING
from .metadata import Metadata
from . import errors

if TYPE_CHECKING:
    from .package import Package
    from .resource import Resource


# NOTE:
# We might consider migrating transform_resource API to emitting
# data as an ouput instead of setting it to target.data
# It might make custom transform steps more eloquent
# This change probably not even breaking because it will be a new
# mode supported by the system (function emiting data instead of returning None)
# We might consider adding `process_schema/row` etc to the Step class


# TODO: support something like "step.transform_resource_row"
class Step(Metadata):
    """Step representation"""

    code: str = "step"

    def __init__(self, descriptor=None):
        super().__init__(descriptor)
        self.setinitial("code", self.code)

    # Transform

    def transform_resource(self, resource: Resource):
        """Transform resource

        Parameters:
            resource (Resource): resource

        Returns:
            resource (Resource): resource
        """
        pass

    def transform_package(self, package: Package):
        """Transform package

        Parameters:
            package (Package): package

        Returns:
            package (Package): package
        """
        pass

    # Convert

    # TODO: review
    @classmethod
    def from_descriptor(cls, descriptor):
        system = import_module("frictionless").system
        return system.create_step(descriptor)

    # Metadata

    metadata_Error = errors.StepError
