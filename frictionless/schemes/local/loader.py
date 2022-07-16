from __future__ import annotations
import io
from ...resource import Loader
from ... import helpers


class LocalLoader(Loader):
    """Local loader implementation."""

    # Read

    def read_byte_stream_create(self):
        scheme = "file://"
        normpath = self.resource.normpath
        if normpath.startswith(scheme):
            normpath = normpath.replace(scheme, "", 1)
        byte_stream = io.open(normpath, "rb")
        return byte_stream

    # Write

    def write_byte_stream(self, path):
        helpers.move_file(path, self.resource.normpath)
