import io
from ..loader import Loader
from .. import config


# TODO: do we support something like "text://id,name\n1,value.csv"?
class TextLoader(Loader):
    """Text loader implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import loaders`

    """

    # Read

    def read_byte_stream_create(self):
        scheme = "text://"
        source = self.resource.source
        if source.startswith(scheme):
            source = source.replace(scheme, "", 1)
        byte_stream = io.BufferedRandom(io.BytesIO())
        byte_stream.write(source.encode(config.DEFAULT_ENCODING))
        byte_stream.seek(0)
        return byte_stream
