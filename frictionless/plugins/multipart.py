import tempfile
from ..resource import Resource
from ..control import Control
from ..plugin import Plugin
from ..loader import Loader
from ..system import system
from .. import helpers
from .. import config


# Plugin


class MultipartPlugin(Plugin):
    """Plugin for Multipart Data

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.multipart import MultipartPlugin`

    """

    def create_file(self, file):
        if file.multipart:
            file.scheme = "multipart"
            return file

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

    def __init__(
        self,
        descriptor=None,
        chunk_size=None,
        newline=None,
        detect_encoding=None,
    ):
        self.setinitial("chunkSize", chunk_size)
        super().__init__(descriptor, newline=newline, detect_encoding=detect_encoding)

    @property
    def chunk_size(self):
        return self.get("chunkSize", config.DEFAULT_MULTIPART_CHUNK_SIZE)

    # Expand

    def expand(self):
        """Expand metadata"""
        super().expand()
        self.setdefault("chunkSize", self.chunk_size)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "properties": {
            "chunkSize": {"type": "number"},
            "newline": {"type": "string"},
            "detectEncoding": {},
        },
    }


# Loader


class MultipartLoader(Loader):
    """Multipart loader implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.multipart import MultipartLoader`

    """

    # Read

    def read_byte_stream_create(self):
        fullpath = self.resource.fullpath
        remote = self.resource.remote
        # TODO: review
        headless = self.resource.get("layout", {}).get("header") is False
        headless = headless or self.resource.format != "csv"
        byte_stream = MultipartByteStream(fullpath, remote=remote, headless=headless)
        return byte_stream

    # Write

    # TODO: raise an exception for csv/header situation?
    def write_byte_stream_save(self, byte_stream):
        number = 0
        while True:
            bytes = byte_stream.read(self.resource.control.chunk_size)
            if not bytes:
                break
            number += 1
            fullpath = self.resource.fullpath.format(number=number)
            with tempfile.NamedTemporaryFile(delete=False) as file:
                file.write(bytes)
            helpers.move_file(file.name, fullpath)


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

    # TODO: review
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

    # TODO: review (this situation with header/no-header/skipping like is not yet clear)
    def read_line_stream(self):
        for number, path in enumerate(self.__path, start=1):
            with system.create_loader(Resource(path=path, trusted=True)) as loader:
                for line_number, line in enumerate(loader.byte_stream, start=1):
                    if not self.__headless and number > 1 and line_number == 1:
                        continue
                    yield line
