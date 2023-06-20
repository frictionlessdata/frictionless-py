from __future__ import annotations

import io

from ... import helpers
from ...system import Loader


class LocalLoader(Loader):
    """Local loader implementation."""

    # Read

    def read_byte_stream_create(self):
        assert self.resource.normpath
        scheme = "file://"
        path = self.resource.normpath
        if path.startswith(scheme):
            path = path.replace(scheme, "", 1)
        byte_stream = io.open(path, "rb")
        return byte_stream

    # Write

    def write_byte_stream(self, path: str):
        assert self.resource.normpath
        helpers.move_file(path, self.resource.normpath)
