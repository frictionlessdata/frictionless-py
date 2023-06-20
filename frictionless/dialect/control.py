from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Optional

import attrs

from .. import errors, settings
from ..metadata import Metadata
from ..platform import platform

if TYPE_CHECKING:
    from .dialect import Dialect


@attrs.define(kw_only=True, repr=False)
class Control(Metadata):
    """Control representation.

    This class is the base class for all the control classes that are
    used to set the states of various different components.

    """

    name: Optional[str] = None
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “_” or “-” characters.
    """

    type: ClassVar[str]
    """
    Type of the control. It could be a zenodo plugin control, csv control etc.
    For example: "csv", "zenodo" etc
    """

    title: Optional[str] = None
    """
    A human-oriented title for the control.
    """

    description: Optional[str] = None
    """
    A brief description of the control.
    """

    # Convert

    @classmethod
    def from_dialect(cls, dialect: Dialect):
        if not dialect.has_control(cls.type):
            dialect.add_control(cls())
        control = dialect.get_control(cls.type)
        assert isinstance(control, cls)
        return control

    def to_dialect(self):
        return platform.frictionless.Dialect(controls=[self])

    # Metadata

    metadata_type = "control"
    metadata_Error = errors.ControlError
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
        return platform.frictionless.system.select_control_class(type)
