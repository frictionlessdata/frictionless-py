from .metadata import Metadata
from . import errors


class Control(Metadata):
    """Control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Control`

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process
    """

    # Metadata

    metadata_Error = errors.ControlError
