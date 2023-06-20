from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Union

import attrs

from .. import errors, settings, types
from ..metadata import Metadata
from ..system import system

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
@attrs.define(kw_only=True, repr=False)
class Step(Metadata):
    """Step representation.

    A base class for all the step subclasses.

    """

    name: Optional[str] = None
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “_” or “-” characters.
    """

    type: ClassVar[str]
    """
    A short url-usable (and preferably human-readable) name/type.
    This MUST be lower-case and contain only alphanumeric characters
    along with “_” or “-” characters. For example: "cell-fill".
    """

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
    def from_descriptor(
        cls, descriptor: Union[str, types.IDescriptor], *args: Any, **kwargs: Any
    ):
        descriptor = cls.metadata_retrieve(descriptor)

        # Type (framework/v4)
        code = descriptor.pop("code", None)
        if code:
            descriptor.setdefault("type", code)
            note = 'Step "code" is deprecated in favor of "type"'
            note += "(it will be removed in the next major version)"
            warnings.warn(note, UserWarning)

        return super().from_descriptor(descriptor, *args, **kwargs)

    # Metadata

    metadata_type = "step"
    metadata_Error = errors.StepError
    metadata_profile = {
        "type": "object",
        "required": ["type"],
        "properties": {
            "name": {"type": "string", "pattern": settings.NAME_PATTERN},
            "type": {"type": "string", "pattern": settings.TYPE_PATTERN},
            "title": {"type": "string"},
            "description": {"type": "string"},
        },
    }

    @classmethod
    def metadata_select_class(cls, type: Optional[str]):
        return system.select_step_class(type)
