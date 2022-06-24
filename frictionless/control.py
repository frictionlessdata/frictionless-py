from importlib import import_module
from .metadata2 import Metadata2
from . import errors


class Control(Metadata2):
    """Control representation"""

    code: str

    # Convert

    # TODO: review
    @classmethod
    def from_descriptor(cls, descriptor):
        if cls is Control:
            descriptor = cls.metadata_normalize(descriptor)
            system = import_module("frictionless").system
            return system.create_control(descriptor)  # type: ignore
        return super().from_descriptor(descriptor)

    # Metadata

    metadata_Error = errors.ControlError
    metadata_defined = {"code"}
