from importlib import import_module
from ..metadata import Metadata
from .. import errors


class Control(Metadata):
    """Control representation"""

    code: str

    # Metadata

    metadata_Error = errors.ControlError

    @classmethod
    def metadata_import(cls, descriptor):
        if cls is Control:
            descriptor = cls.metadata_normalize(descriptor)
            system = import_module("frictionless").system
            return system.create_control(descriptor)  # type: ignore
        return super().metadata_import(descriptor)
