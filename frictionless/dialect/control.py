from __future__ import annotations
import attrs
from importlib import import_module
from typing import TYPE_CHECKING, ClassVar, Optional
from ..metadata import Metadata
from .. import settings
from .. import errors

if TYPE_CHECKING:
    from .dialect import Dialect


@attrs.define(kw_only=True)
class Control(Metadata):
    """Control representation"""

    type: ClassVar[str]
    """NOTE: add docs"""

    # State

    title: Optional[str] = None
    """NOTE: add docs"""

    description: Optional[str] = None
    """NOTE: add docs"""

    @classmethod
    def from_dialect(cls, dialect: Dialect):

        # Add control
        if not dialect.has_control(cls.type):
            dialect.add_control(cls())

        control = dialect.get_control(cls.type)
        assert isinstance(control, cls)
        return control

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
            system = import_module("frictionless").system
            return system.select_Control(type)
