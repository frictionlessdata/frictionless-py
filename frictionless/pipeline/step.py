from __future__ import annotations
import attrs
import warnings
from typing import TYPE_CHECKING, ClassVar, Optional
from ..metadata import Metadata
from ..system import system
from .. import settings
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
@attrs.define(kw_only=True)
class Step(Metadata):
    """Step representation.

    A base class for all the step subclasses.

    """

    type: ClassVar[str]
    """
    A short url-usable (and preferably human-readable) name/type.
    This MUST be lower-case and contain only alphanumeric characters
    along with “_” or “-” characters. For example: "cell-fill".
    """

    # State

    title: Optional[str] = None
    """
    A human-oriented title for the Step.
    """

    description: Optional[str] = None
    """
    A brief description of the Step.
    """

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

    @classmethod
    def from_descriptor(cls, descriptor):

        # Type (framework/v4)
        code = descriptor.pop("code", None)
        if code:
            descriptor.setdefault("type", code)
            note = 'Step "code" is deprecated in favor of "type"'
            note += "(it will be removed in the next major version)"
            warnings.warn(note, UserWarning)

        return super().from_descriptor(descriptor)

    # Metadata

    metadata_type = "step"
    metadata_Error = errors.StepError
    metadata_profile = {
        "type": "object",
        "required": ["type"],
        "properties": {
            "type": {"type": "string", "pattern": settings.TYPE_PATTERN},
            "title": {"type": "string"},
            "description": {"type": "string"},
        },
    }

    @classmethod
    def metadata_specify(cls, *, type=None, property=None):
        if type is not None:
            return system.select_Step(type)
