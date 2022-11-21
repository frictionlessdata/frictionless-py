from __future__ import annotations
import io
import os
import shutil
import atexit
import hashlib
import tempfile
from typing import TYPE_CHECKING, Optional, Any
from ..exception import FrictionlessException
from ..platform import platform
from ..stats import Stats
from .. import settings
from .. import errors

if TYPE_CHECKING:
    from ..resource import Resource
    from ..interfaces import IBuffer, IByteStream, ITextStream


# NOTE:
# Probably we need to rework the way we calculate stats
# First of all, it's not really reliable as read/read1(size) can be called many times
# Secondly, for now, we stream compressed files twice (see loader.read_byte_stream_decompress)
# Although, we need to reviw how we collect buffer - cab it be less IO operations?


# TODO: migrate to dataclass?
class Loader:
    """Loader representation

    Parameters:
        resource (Resource): resource

    """

    remote: bool = False
    """
    Specifies if the resource is remote.
    """

    def __init__(self, resource: Resource):
        self.__resource: Resource = resource
        self.__buffer: Optional[IBuffer] = None
        self.__byte_stream: Optional[IByteStream] = None
        self.__text_stream: Optional[ITextStream] = None

    def __enter__(self):
        if self.closed:
            self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    # Props

    @property
    def resource(self) -> Resource:
        """
        Returns:
            resource (Resource): resource
        """
        return self.__resource

    @property
    def buffer(self) -> IBuffer:
        """
        Returns:
            Loader: buffer
        """
        if self.__buffer is None:
            raise FrictionlessException("loader is not open")
        return self.__buffer

    @property
    def byte_stream(self) -> IByteStream:
        """Resource byte stream

        The stream is available after opening the loader

        Returns:
            io.ByteStream: resource byte stream
        """
        if self.__byte_stream is None:
            raise FrictionlessException("loader is not open")
        return self.__byte_stream

    @property
    def text_stream(self) -> ITextStream:
        """Resource text stream

        The stream is available after opening the loader

        Returns:
            io.TextStream: resource text stream
        """
        if self.closed:
            raise FrictionlessException("loader is not open")
        if not self.__text_stream:
            self.__text_stream = self.read_text_stream()
        return self.__text_stream

    # Open/Close

    def open(self):
        """Open the loader as "io.open" does"""
        self.close()
        try:
            self.__byte_stream = self.read_byte_stream()
            return self
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        """Close the loader as "filelike.close" does"""
        if self.__byte_stream:
            self.__byte_stream.close()
        self.__byte_stream = None

    @property
    def closed(self) -> bool:
        """Whether the loader is closed

        Returns:
            bool: if closed
        """
        return self.__byte_stream is None

    # Read

    def read_byte_stream(self) -> IByteStream:
        """Read bytes stream

        Returns:
            io.ByteStream: resource byte stream
        """
        try:
            byte_stream = self.read_byte_stream_create()
            byte_stream = self.read_byte_stream_process(byte_stream)
            byte_stream = self.read_byte_stream_decompress(byte_stream)  # type: ignore
            buffer = self.read_byte_stream_buffer(byte_stream)
            self.read_byte_stream_analyze(buffer)
            self.__buffer = buffer
        except (LookupError, UnicodeDecodeError) as exception:
            error = errors.EncodingError(note=str(exception))
            raise FrictionlessException(error) from exception
        except (platform.zipfile.BadZipFile, platform.gzip.BadGzipFile) as exception:
            error = errors.CompressionError(note=str(exception))
            raise FrictionlessException(error)
        except IOError as exception:
            error = errors.SchemeError(note=str(exception))
            raise FrictionlessException(error)
        return byte_stream

    def read_byte_stream_create(self) -> IByteStream:
        """Create bytes stream

        Returns:
            io.ByteStream: resource byte stream
        """
        raise NotImplementedError()

    def read_byte_stream_process(
        self,
        byte_stream: IByteStream,
    ) -> ByteStreamWithStatsHandling:
        """Process byte stream

        Parameters:
            byte_stream (io.ByteStream): resource byte stream

        Returns:
            io.ByteStream: resource byte stream
        """
        return ByteStreamWithStatsHandling(byte_stream, stats=self.resource.stats)

    def read_byte_stream_decompress(self, byte_stream: IByteStream) -> IByteStream:
        """Decompress byte stream

        Parameters:
            byte_stream (io.ByteStream): resource byte stream

        Returns:
            io.ByteStream: resource byte stream
        """

        # ZIP compression
        if self.resource.compression == "zip":
            # Remote
            if self.remote:
                self.remote = False
                target = tempfile.NamedTemporaryFile()
                shutil.copyfileobj(byte_stream, target)
                target.seek(0)
                byte_stream = target  # type: ignore
            # Stats
            else:
                bytes = True
                while bytes:
                    bytes = byte_stream.read1(io.DEFAULT_BUFFER_SIZE)  # type: ignore
                byte_stream.seek(0)
            # Unzip
            with platform.zipfile.ZipFile(byte_stream) as archive:
                name = self.resource.innerpath or archive.namelist()[0]
                if not name:
                    error = errors.Error(note="the arhive is empty")
                    raise FrictionlessException(error)
                # TODO: enable typing when resource.innerpath is fixed
                with archive.open(name) as file:  # type: ignore
                    target = tempfile.NamedTemporaryFile()
                    shutil.copyfileobj(file, target)
                    target.seek(0)
                byte_stream = target  # type: ignore
                self.resource.innerpath = name
            return byte_stream

        # GZip compression
        if self.resource.compression == "gz":
            # Stats
            if not self.remote:
                bytes = True
                while bytes:
                    bytes = byte_stream.read1(io.DEFAULT_BUFFER_SIZE)  # type: ignore
                byte_stream.seek(0)
            byte_stream = platform.gzip.open(byte_stream)  # type: ignore
            return byte_stream

        # No compression
        if not self.resource.compression:
            return byte_stream

        # Not supported compression
        note = f'compression "{self.resource.compression}" is not supported'
        raise FrictionlessException(errors.CompressionError(note=note))

    def read_byte_stream_buffer(self, byte_stream):
        """Buffer byte stream

        Parameters:
            byte_stream (io.ByteStream): resource byte stream

        Returns:
            bytes: buffer
        """
        buffer = byte_stream.read(self.resource.detector.buffer_size)
        buffer = buffer[: self.resource.detector.buffer_size]
        byte_stream.seek(0)
        return buffer

    def read_byte_stream_analyze(self, buffer):
        """Detect metadta using sample

        Parameters:
            buffer (bytes): byte buffer
        """
        self.resource.encoding = self.resource.detector.detect_encoding(
            buffer, encoding=self.resource.get_defined("encoding")
        )

    def read_text_stream(self):
        """Read text stream

        Returns:
            io.TextStream: resource text stream
        """
        # NOTE: this solution might be improved using parser properties
        newline = "" if self.resource.format == "csv" else None
        # TODO: enable typing when resource.encodign is fixed
        return io.TextIOWrapper(self.byte_stream, self.resource.encoding, newline=newline)  # type: ignore

    # Write

    def write_byte_stream(self, path) -> Any:
        """Write from a temporary file

        Parameters:
            path (str): path to a temporary file

        Returns:
            any: result of writing e.g. resulting path
        """
        byte_stream = self.write_byte_stream_create(path)
        result = self.write_byte_stream_save(byte_stream)
        return result

    def write_byte_stream_create(self, path) -> IByteStream:
        """Create byte stream for writing

        Parameters:
            path (str): path to a temporary file

        Returns:
            io.ByteStream: byte stream
        """
        atexit.register(os.remove, path)
        file = open(path, "rb")
        return file

    def write_byte_stream_save(self, byte_stream) -> Any:
        """Store byte stream"""
        raise NotImplementedError()


# Internal


# NOTE:
# We can try buffering byte buffer especially for remote
# Also, currently read/read1/item implementation is not complete
# As an option, we can think of subclassing some io.* class


class ByteStreamWithStatsHandling:
    def __init__(self, byte_stream: IByteStream, *, stats: Stats):
        self.__byte_stream = byte_stream
        self.__stats = stats
        self.__md5 = hashlib.new("md5")
        self.__sha256 = hashlib.new("sha256")
        self.__bytes = 0

    def __getattr__(self, name):
        return getattr(self.__byte_stream, name)

    def __iter__(self):
        while True:
            bytes = self.read1(settings.DEFAULT_BUFFER_SIZE)
            if not bytes:
                break
            yield from bytes.splitlines(keepends=True)

    @property
    def closed(self):
        return self.__byte_stream.closed

    def read1(self, size=-1):
        size = -1 if size is None else size
        chunk = self.__byte_stream.read1(size)  # type: ignore

        # Calculate
        self.__md5.update(chunk)
        self.__sha256.update(chunk)
        self.__bytes += len(chunk)

        # Store (hash on EOF)
        if size == -1 or not chunk:
            self.__stats.md5 = self.__md5.hexdigest()
            self.__stats.sha256 = self.__sha256.hexdigest()
        self.__stats.bytes = self.__bytes

        return chunk
