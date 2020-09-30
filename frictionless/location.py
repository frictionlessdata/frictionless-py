import os
from urllib.request import urlopen
from . import exceptions
from . import helpers
from . import errors
from . import config


class Location:
    def __init__(self, resource):

        # Detect source
        if resource.data:
            source = resource.data
        elif isinstance(resource.path, str):
            source = resource.path
            if helpers.is_remote_path(source):
                source = os.path.join(resource.basepath, resource.path)
        elif isinstance(resource.path, list):
            source = MultipartSource(
                source,
                basepath=resource.basepath,
                headless=resource.get("dialect", {}).get("header") is False,
            )

        # Detect source/scheme/format/compression/compression_path
        detect = helpers.detect_source_scheme_and_format(source)
        self.__compression = config.DEFAULT_COMPRESSION
        self.__compression_path = config.DEFAULT_COMPRESSION_PATH
        if detect[1] in config.COMPRESSION_FORMATS:
            self.__compression = detect[1]
            source = source[: -len(detect[1]) - 1]
            if resource.get("compression_path"):
                source = os.path.join(source, resource.get("compression_path"))
            detect = helpers.detect_source_scheme_and_format(source)
        self.__scheme = detect[0] or config.DEFAULT_SCHEME
        self.__format = detect[1] or config.DEFAULT_FORMAT

        # Save source
        self.__source = source

    @property
    def source(self):
        return self.__source

    @property
    def scheme(self):
        return self.__scheme

    @property
    def format(self):
        return self.__format

    @property
    def compression(self):
        return self.__compression

    @property
    def compression_path(self):
        return self.__compression_path

    @property
    def inline(self):
        if self.multipart:
            return False
        return isinstance(self.source, str)

    @property
    def multipart(self):
        return isinstance(self.source, MultipartSource)

    @property
    def remote(self):
        if self.inline:
            return False
        if self.multipart:
            return self.source.remote
        return helpers.is_remote_path(self.source)

    @property
    def suspect(self):
        if self.inline:
            return False
        if self.multipart:
            return any(not helpers.is_safe_path(path) for path in self.source)
        return not helpers.is_safe_path(self.source)


# Internal


class MultipartSource:
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
            streams = (urlopen(path) for path in self.__path)
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
