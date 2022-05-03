import io
from ...loader import Loader
from ... import helpers


class LocalLoader(Loader):
    """Local loader implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.local import LocalLoader`

    """

    # Read

    def read_byte_stream_create(self):
        scheme = "file://"
        fullpath = self.resource.fullpath
        if fullpath.startswith(scheme):
            fullpath = fullpath.replace(scheme, "", 1)
        byte_stream = io.open(fullpath, "rb")
        return byte_stream

    # Write

    def write_byte_stream(self, path):
        helpers.move_file(path, self.resource.fullpath)
