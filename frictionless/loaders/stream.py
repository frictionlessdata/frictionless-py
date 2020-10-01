from ..loader import Loader
from .. import exceptions
from .. import errors


class StreamLoader(Loader):
    """Stream loader implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import loaders`

    """

    # Read

    def read_byte_stream_create(self):
        source = self.resource.source
        if hasattr(source, "encoding"):
            error = errors.SchemeError(note="only byte streams are supported")
            raise exceptions.FrictionlessException(error)
        return source
