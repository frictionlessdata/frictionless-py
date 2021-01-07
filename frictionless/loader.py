import io
import os
import gzip
import codecs
import shutil
import atexit
import hashlib
import zipfile
import tempfile
from .exception import FrictionlessException
from . import errors
from . import config


# TODO
# Probably we need to rework the way we calculate stats
# First of all, it's not really reliable as read/read1(size) can be called many times
# Secondly, for now, we stream compressed files twice (see loader.read_byte_stream_decompress)


class Loader:
    """Loader representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Loader`

    Parameters:
        resource (Resource): resource

    """

    remote = False

    def __init__(self, resource):
        self.__resource = resource
        self.__byte_stream = None
        self.__text_stream = None

    def __enter__(self):
        if self.closed:
            self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    @property
    def resource(self):
        """
        Returns:
            resource (Resource): resource
        """
        return self.__resource

    @property
    def byte_stream(self):
        """Resource byte stream

        The stream is available after opening the loader

        Returns:
            io.ByteStream: resource byte stream
        """
        return self.__byte_stream

    @property
    def text_stream(self):
        """Resource text stream

        The stream is available after opening the loader

        Returns:
            io.TextStream: resource text stream
        """
        if not self.__text_stream:
            self.__text_stream = self.read_text_stream()
        return self.__text_stream

    # Open/Close

    def open(self):
        """Open the loader as "io.open" does"""
        self.close()
        if self.__resource.control.metadata_errors:
            error = self.__resource.control.metadata_errors[0]
            raise FrictionlessException(error)
        try:
            self.__byte_stream = self.read_byte_stream()
            return self
        except Exception:
            self.close()
            raise

    def close(self):
        """Close the loader as "filelike.close" does"""
        if self.__byte_stream:
            self.__byte_stream.close()
        self.__byte_stream = None

    @property
    def closed(self):
        """Whether the loader is closed

        Returns:
            bool: if closed
        """
        return self.__byte_stream is None

    # Read

    def read_byte_stream(self):
        """Read bytes stream

        Returns:
            io.ByteStream: resource byte stream
        """
        try:
            byte_stream = self.read_byte_stream_create()
            byte_stream = self.read_byte_stream_infer_stats(byte_stream)
            byte_stream = self.read_byte_stream_decompress(byte_stream)
        except IOError as exception:
            error = errors.SchemeError(note=str(exception))
            raise FrictionlessException(error)
        except config.COMPRESSION_EXCEPTIONS as exception:
            error = errors.CompressionError(note=str(exception))
            raise FrictionlessException(error)
        return byte_stream

    def read_byte_stream_create(self):
        """Create bytes stream

        Returns:
            io.ByteStream: resource byte stream
        """
        raise NotImplementedError()

    def read_byte_stream_infer_stats(self, byte_stream):
        """Infer byte stream stats

        Parameters:
            byte_stream (io.ByteStream): resource byte stream

        Returns:
            io.ByteStream: resource byte stream
        """
        if not self.resource.get("stats"):
            return byte_stream
        return ByteStreamWithStatsHandling(byte_stream, resource=self.resource)

    def read_byte_stream_decompress(self, byte_stream):
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
                byte_stream = target
            # Stats
            else:
                bytes = True
                while bytes:
                    bytes = byte_stream.read1(io.DEFAULT_BUFFER_SIZE)
                byte_stream.seek(0)
            # Unzip
            with zipfile.ZipFile(byte_stream) as archive:
                name = self.resource.innerpath or archive.namelist()[0]
                with archive.open(name) as file:
                    target = tempfile.NamedTemporaryFile()
                    shutil.copyfileobj(file, target)
                    target.seek(0)
                byte_stream = target
                self.resource.innerpath = name
            return byte_stream

        # GZip compression
        if self.resource.compression == "gz":
            # Stats
            if not self.remote:
                bytes = True
                while bytes:
                    bytes = byte_stream.read1(io.DEFAULT_BUFFER_SIZE)
                byte_stream.seek(0)
            byte_stream = gzip.open(byte_stream)
            return byte_stream

        # No compression
        if not self.resource.compression:
            return byte_stream

        # Not supported compression
        note = f'compression "{self.resource.compression}" is not supported'
        raise FrictionlessException(errors.CompressionError(note=note))

    def read_text_stream(self):
        """Read text stream

        Returns:
            io.TextStream: resource text stream
        """
        try:
            self.read_text_stream_infer_encoding(self.byte_stream)
        except (LookupError, UnicodeDecodeError) as exception:
            error = errors.EncodingError(note=str(exception))
            raise FrictionlessException(error) from exception
        return self.read_text_stream_decode(self.byte_stream)

    def read_text_stream_infer_encoding(self, byte_stream):
        """Infer text stream encoding

        Parameters:
            byte_stream (io.ByteStream): resource byte stream
        """
        control = self.resource.control
        # We don't need a detected encoding
        encoding = self.resource.get("encoding")
        sample = byte_stream.read(config.DEFAULT_INFER_ENCODING_VOLUME)
        sample = sample[: config.DEFAULT_INFER_ENCODING_VOLUME]
        byte_stream.seek(0)
        if encoding is None:
            encoding = control.detect_encoding(sample)
        encoding = codecs.lookup(encoding).name
        # Work around for incorrect inferion of utf-8-sig encoding
        if encoding == "utf-8":
            if sample.startswith(codecs.BOM_UTF8):
                encoding = "utf-8-sig"
        # Use the BOM stripping name (without byte-order) for UTF-16 encodings
        elif encoding == "utf-16-be":
            if sample.startswith(codecs.BOM_UTF16_BE):
                encoding = "utf-16"
        elif encoding == "utf-16-le":
            if sample.startswith(codecs.BOM_UTF16_LE):
                encoding = "utf-16"
        self.resource.encoding = encoding

    def read_text_stream_decode(self, byte_stream):
        """Decode text stream

        Parameters:
            byte_stream (io.ByteStream): resource byte stream

        Returns:
            text_stream (io.TextStream): resource text stream
        """
        return io.TextIOWrapper(
            byte_stream, self.resource.encoding, newline=self.resource.control.newline
        )

    # Write

    def write_byte_stream(self, path):
        """Write from a temporary file

        Parameters:
            path (str): path to a temporary file

        Returns:
            any: result of writing e.g. resulting path
        """
        byte_stream = self.write_byte_stream_create(path)
        result = self.write_byte_stream_save(byte_stream)
        return result

    def write_byte_stream_create(self, path):
        """Create byte stream for writing

        Parameters:
            path (str): path to a temporary file

        Returns:
            io.ByteStream: byte stream
        """
        atexit.register(os.remove, path)
        file = open(path, "rb")
        return file

    def write_byte_stream_save(self, byte_stream):
        """Store byte stream"""
        raise NotImplementedError()


# Internal


class ByteStreamWithStatsHandling:
    # TODO
    # We can try buffering byte sample especially for remote
    # Also, currently read/read1/item implementation is not complete
    # As an option, we can think of subclassing some io.* class

    def __init__(self, byte_stream, *, resource):
        try:
            self.__hasher = hashlib.new(resource.hashing) if resource.hashing else None
        except Exception as exception:
            error = errors.HashingError(note=str(exception))
            raise FrictionlessException(error)
        # TODO: document why we ignore stats if there is hash
        self.__stats = resource.stats if not resource.stats["hash"] else {}
        self.__byte_stream = byte_stream

    def __getattr__(self, name):
        return getattr(self.__byte_stream, name)

    @property
    def closed(self):
        return self.__byte_stream.closed

    def read1(self, size=-1):
        chunk = self.__byte_stream.read1(size)
        self.__stats["bytes"] += len(chunk)
        if self.__hasher:
            self.__hasher.update(chunk)
            self.__stats["hash"] = self.__hasher.hexdigest()
        return chunk
