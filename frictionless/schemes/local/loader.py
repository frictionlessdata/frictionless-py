from __future__ import annotations
import io
from ...system import Loader
from ... import helpers


class LocalLoader(Loader):
    """Local loader implementation."""

    # Read

    def read_byte_stream_create(self):
        scheme = "file://"
        path = self.resource.normpath
        if path.startswith(scheme):
            path = path.replace(scheme, "", 1)
        byte_stream = io.open(path, "rb")
        return byte_stream

    # Write

    def write_byte_stream(self, path):
        helpers.move_file(path, self.resource.normpath)
