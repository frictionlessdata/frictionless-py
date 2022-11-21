from __future__ import annotations
import tempfile
from .control import MultipartControl
from ...resource import Resource
from ...system import Loader
from ... import helpers


# NOTE:
# Curretnly the situation with header/no-header concatenation is complicated
# We need to review it and add more tests for general/tabular edge cases


class MultipartLoader(Loader):
    """Multipart loader implementation."""

    # Read

    def read_byte_stream_create(self):
        remote = self.resource.remote
        headless = self.resource.dialect.header is False
        headless = headless or self.resource.format != "csv"
        return MultipartByteStream(
            self.resource.normpaths,
            remote=remote,
            headless=headless,
        )

    # Write

    def write_byte_stream_save(self, byte_stream):
        control = MultipartControl.from_dialect(self.resource.dialect)
        number = 0
        while True:
            bytes = byte_stream.read(control.chunk_size)
            if not bytes:
                break
            number += 1
            path = self.resource.normpath.format(number=number)
            with tempfile.NamedTemporaryFile(delete=False) as file:
                file.write(bytes)
            helpers.move_file(file.name, path)


# Internal


class MultipartByteStream:
    def __init__(self, paths, *, remote, headless):
        self.__paths = paths
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
        for number, path in enumerate(self.__paths, start=1):
            with Resource(path=path).open(as_file=True) as resource:
                for line_number, line in enumerate(resource.byte_stream, start=1):
                    if not self.__headless and number > 1 and line_number == 1:
                        continue
                    yield line
