from ..exception import FrictionlessException
from ..resource import Resource
from ..control import Control
from ..plugin import Plugin
from ..loader import Loader
from ..system import system
from .. import errors


# Plugin


class MultipartPlugin(Plugin):
    """Plugin for Multipart Data

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.multipart import MultipartPlugin`

    """

    def create_control(self, resource, *, descriptor):
        if resource.scheme == "multipart":
            return MultipartControl(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "multipart":
            return MultipartLoader(resource)


# Control


class MultipartControl(Control):
    """Multipart control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.multipart import MultipartControl`

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    pass


# Loader


class MultipartLoader(Loader):
    """Multipart loader implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.multipart import MultipartLoader`

    """

    # Read

    def read_byte_stream_create(self):
        source = self.resource.source
        remote = self.resource.remote
        headless = self.resource.get("dialect", {}).get("header") is False
        byte_stream = MultipartByteStream(source, remote=remote, headless=headless)
        return byte_stream

    # Write

    def write_byte_stream_save(self, byte_stream):
        error = errors.SchemeError(note="Writing to Multipart Data is not supported")
        raise FrictionlessException(error)


# Internal


class MultipartByteStream:
    def __init__(self, path, *, remote, headless):
        self.__path = path
        self.__remote = remote
        self.__headless = headless
        self.__line_stream = self.read_line_stream()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def __iter__(self):
        return self.__line_stream

    @property
    def remote(self):
        return self.__remote

    @property
    def closed(self):
        return False

    def readable(self):
        return True

    def seekable(self):
        return True

    def writable(self):
        return False

    def close(self):
        pass

    def flush(self):
        pass

    def read1(self, size):
        return self.read(size)

    def seek(self, offset):
        assert offset == 0
        self.__line_stream = self.read_line_stream()

    def read(self, size):
        res = b""
        while True:
            try:
                res += next(self.__line_stream)
            except StopIteration:
                break
            if len(res) > size:
                break
        return res

    def read_line_stream(self):
        for number, path in enumerate(self.__path, start=1):
            with system.create_loader(Resource(path=path)) as loader:
                for line_number, line in enumerate(loader.byte_stream, start=1):
                    if not line.endswith(b"\n"):
                        line += b"\n"
                    if not self.__headless and number > 1 and line_number == 1:
                        continue
                    yield line
