import io
from ..control import Control
from ..plugin import Plugin
from ..loader import Loader


# Plugin


class BufferPlugin(Plugin):
    """Plugin for Buffer Data

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.local import BufferPlugin`

    """

    code = "buffer"

    def create_file(self, file):
        if not file.scheme and not file.format:
            if isinstance(file.data, bytes):
                file.scheme = "buffer"
                file.format = ""
                return file

    def create_control(self, resource, *, descriptor):
        if resource.scheme == "buffer":
            return BufferControl(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "buffer":
            return BufferLoader(resource)


# Control


class BufferControl(Control):
    """Buffer control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.buffer import BufferControl`

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
    }


# Loader


class BufferLoader(Loader):
    """Buffer loader implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.buffer import BufferLoader`

    """

    # Read

    def read_byte_stream_create(self):
        byte_stream = io.BufferedRandom(io.BytesIO())
        byte_stream.write(self.resource.data)
        byte_stream.seek(0)
        return byte_stream

    # Write

    def write_byte_stream_save(self, byte_stream):
        self.resource.data = byte_stream.read()
