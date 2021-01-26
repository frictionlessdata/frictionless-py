from .metadata import Metadata
from . import errors


class Dialect(Metadata):
    """Dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Dialect`

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process
    """

    # Metadata

    metadata_Error = errors.DialectError
