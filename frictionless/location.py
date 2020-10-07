import os
from urllib.request import urlopen
from . import helpers
from . import config


# TODO: Normalize detection functions
# TODO: Merge into Resource when MultipartSource is moved?
class Location:
    def __init__(self, resource):

        # Detect source
        source = []
        if resource.data is not None:
            source = resource.data
        elif isinstance(resource.path, str):
            source = resource.path
            if not helpers.is_remote_path(source):
                source = os.path.join(resource.basepath, resource.path)
        elif isinstance(resource.path, list):
            basepath = resource.basepath
            headless = resource.get("dialect", {}).get("header") is False
            source = MultipartSource(resource.path, basepath=basepath, headless=headless)

        # Detect scheme/format/compression/compression_path
        name = helpers.detect_name(source)
        detect = helpers.detect_source_scheme_and_format(source)
        compression = config.DEFAULT_COMPRESSION
        compression_path = config.DEFAULT_COMPRESSION_PATH
        if detect[1] in config.COMPRESSION_FORMATS:
            compression = detect[1]
            new_source = source[: -len(detect[1]) - 1]
            if resource.get("compression_path"):
                new_source = os.path.join(new_source, resource.get("compression_path"))
            detect = helpers.detect_source_scheme_and_format(new_source)
        scheme = detect[0] or config.DEFAULT_SCHEME
        format = detect[1] or config.DEFAULT_FORMAT

        # Set attributes
        self.__name = name
        self.__source = source
        self.__scheme = scheme
        self.__format = format
        self.__compression = compression
        self.__compression_path = compression_path

    @property
    def source(self):
        return self.__source

    @property
    def name(self):
        return self.__name

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
        return not isinstance(self.source, str)

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


# Internal


# TODO: move it to Table/LocalLoader?
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
