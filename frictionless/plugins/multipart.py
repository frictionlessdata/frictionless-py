import os
from urllib.request import urlopen
from ..loader import Loader
from ..plugin import Plugin
from ..control import Control
from .. import helpers


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

    pass


# Internal


class MultipartByteStream:
    def __init__(self, path, *, basepath, headless):
        self.__path = path
        self.__basepath = basepath
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
        if not self.__path:
            return False
        if self.__basepath:
            return helpers.is_remote_path(self.__basepath)
        return helpers.is_remote_path(self.__path[0])

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
        streams = []
        if self.remote:
            paths = []
            for path in self.__path:
                path = path
                if not helpers.is_remote_path(path):
                    path = os.path.join(self.__basepath, path)
                paths.append(path)
            streams = (urlopen(path) for path in paths)
        else:
            process = lambda path: open(os.path.join(self.__basepath, path), "rb")
            streams = (process(path) for path in self.__path)
        for stream_number, stream in enumerate(streams, start=1):
            for line_number, line in enumerate(stream, start=1):
                if not line.endswith(b"\n"):
                    line += b"\n"
                if not self.__headless and stream_number > 1 and line_number == 1:
                    continue
                yield line
