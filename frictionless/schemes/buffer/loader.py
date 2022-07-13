# type: ignore
from __future__ import annotations
import io
from ...resource import Loader


class BufferLoader(Loader):
    """Buffer loader implementation."""

    # Read

    def read_byte_stream_create(self):
        byte_stream = io.BufferedRandom(io.BytesIO())
        byte_stream.write(self.resource.data)
        byte_stream.seek(0)
        return byte_stream

    # Write

    def write_byte_stream_save(self, byte_stream):
        self.resource.data = byte_stream.read()
