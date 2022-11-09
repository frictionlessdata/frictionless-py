from __future__ import annotations
import attrs
from typing import TYPE_CHECKING, ClassVar, Optional
from ..platform import platform
from ..metadata import Metadata
from .. import settings
from .. import errors

if TYPE_CHECKING:
    from .dialect import Dialect


@attrs.define(kw_only=True)
class Control(Metadata):
    """Control representation.

    This class is the base class for all the control classes that are
    used to set the states of various different components.

    """

    type: ClassVar[str]
    """
    Type of the control. It could be a zenodo plugin control, csv control etc.
    For example: "csv", "zenodo" etc
    """

    # State

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
            "type": {"type": "string", "pattern": settings.TYPE_PATTERN},
            "title": {"type": "string"},
            "description": {"type": "string"},
        },
    }

    @classmethod
    def metadata_specify(cls, *, type=None, property=None):
        if type is not None:
            return platform.frictionless.system.select_Control(type)
