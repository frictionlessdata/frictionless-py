from .metadata import Metadata
from . import helpers
from . import errors


class Control(Metadata):
    """Control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Control`

    Parameters:
        descriptor? (str|dict): descriptor
        newline? (str): a string to be used for `io.open(..., newline=newline)`
        detectEncoding? (func):  a function to detect encoding `(sample) -> encoding`

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, *, newline=None, detect_encoding=None):
        self.setinitial("newline", newline)
        self.setinitial("detectEncoding", detect_encoding)
        super().__init__(descriptor)

    @Metadata.property
    def newline(self):
        """
        Returns:
            str: a string to be used for `io.open(..., newline=newline)`
        """
        return self.get("newline")

    @Metadata.property
    def detect_encoding(self):
        """
        Returns:
            func: detect encoding function
        """
        return self.get("detectEncoding", helpers.detect_encoding)

    # Expand

    def expand(self):
        pass

    # Metadata

    metadata_Error = errors.ControlError
    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "newline": {"type": "string"},
            "detectEncoding": {},
        },
    }
