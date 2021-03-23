import os
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
        byte_stream = self.resource.data
        if not os.path.isfile(byte_stream.name):
            note = f"only local streams are supported: {byte_stream}"
            raise FrictionlessException(errors.SchemeError(note=note))
        if hasattr(byte_stream, "encoding"):
            try:
                byte_stream = open(byte_stream.name, "rb")
            except Exception:
                note = f"cannot open a stream in the byte mode: {byte_stream}"
                raise FrictionlessException(errors.SchemeError(note=note))
        byte_stream = ReusableByteStream(byte_stream)
        return byte_stream

    # Write

    def write_byte_stream_save(self, byte_stream):
        self.resource.data = byte_stream


# Internal


class ReusableByteStream:
    def __init__(self, byte_stream):
        self.__byte_stream = byte_stream

    def __getattr__(self, name):
        return getattr(self.__byte_stream, name)

    def read(self, size=-1):
        if self.__byte_stream.closed:
            try:
                self.__byte_stream = open(self.__byte_stream.name, "rb")
            except Exception:
                note = "cannot re-open a byte stream: {self.__byte_stream}"
                raise FrictionlessException(errors.SchemeError(note=note))
        return self.__byte_stream.read(size)
