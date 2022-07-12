from __future__ import annotations
from typing import TYPE_CHECKING
from ..metadata import Metadata
from ..system import system
from .. import errors

if TYPE_CHECKING:
    from ..package import Package
    from ..resource import Resource


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

    type: str = "step"

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

    # Metadata

    metadata_Error = errors.StepError

    @classmethod
    def metadata_import(cls, descriptor):
        if cls is Step:
            descriptor = cls.metadata_normalize(descriptor)
            return system.create_step(descriptor)  # type: ignore
        return super().metadata_import(descriptor)
