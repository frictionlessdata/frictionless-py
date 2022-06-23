from .metadata2 import Metadata2
from . import errors


# TODO: implement to_dialect helper?
class Control(Metadata2):
    """Control representation"""

    code: str

    # Metadata

    metadata_Error = errors.ControlError
    metadata_defined = {"code"}
