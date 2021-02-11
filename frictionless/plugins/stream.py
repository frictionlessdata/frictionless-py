from ..plugin import Plugin
from ..loader import Loader
from ..control import Control
from ..exception import FrictionlessException
from .. import errors


# Plugin


class StreamPlugin(Plugin):
    """Plugin for Local Data

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.stream import StreamPlugin`

    """

    code = "stream"

    def create_file(self, file):
        if not file.scheme and not file.format:
            if hasattr(file.data, "read"):
                file.scheme = "stream"
                file.format = ""
                return file

    def create_control(self, resource, *, descriptor):
        if resource.scheme == "stream":
            return StreamControl(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "stream":
            return StreamLoader(resource)


# Control


class StreamControl(Control):
    """Stream control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.stream import StreamControl`

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


class StreamLoader(Loader):
    """Stream loader implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.stream import StreamLoader`

    """

    # Read

    def read_byte_stream_create(self):
        data = self.resource.data
        if hasattr(data, "encoding"):
            error = errors.SchemeError(note="only byte streams are supported")
            raise FrictionlessException(error)
        return data

    # Write

    def write_byte_stream_save(self, byte_stream):
        self.resource.data = byte_stream
