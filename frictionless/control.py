from __future__ import annotations
from .metadata2 import Metadata2
from . import errors


class Control(Metadata2):
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
