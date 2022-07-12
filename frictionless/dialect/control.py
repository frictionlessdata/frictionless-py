from __future__ import annotations
from typing import Optional, ClassVar
from dataclasses import dataclass
from typing import TYPE_CHECKING
from importlib import import_module
from ..metadata import Metadata
from .. import errors

if TYPE_CHECKING:
    from .dialect import Dialect


@dataclass
class Control(Metadata):
    """Control representation"""

    type: ClassVar[str]

    # State

    name: Optional[str] = None

    # Convert

    @classmethod
    def from_dialect(cls, dialect: Dialect):
        if not dialect.has_control(cls.type):
            dialect.add_control(cls())
        control = dialect.get_control(cls.type)
        assert isinstance(control, cls)
        return control

    # Metadata

    metadata_Error = errors.ControlError
    metadata_profile = {
        "type": "object",
        "properties": {
            "name": {},
            "type": {},
        },
    }

    @classmethod
    def metadata_import(cls, descriptor):
        if cls is Control:
            descriptor = cls.metadata_normalize(descriptor)
            system = import_module("frictionless").system
            return system.create_control(descriptor)  # type: ignore
        return super().metadata_import(descriptor)
