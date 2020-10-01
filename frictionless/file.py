import shutil
import tempfile
from .system import system
from .resource import Resource
from . import exceptions
from . import helpers
from . import errors


class File:
    """File representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import File`

    Under the hood, File uses available loaders so it can open from local, remote,
    and any other supported schemes

    ```python
    from frictionless import File

    with File('data/text.txt') as file:
        file.read_text()
    ```

    Parameters:
        source (any): file source
        scheme? (str): file scheme
        format? (str): file format
        hashing? (str): file hashing
        encoding? (str): file encoding
        compression? (str): file compression
        compression_path? (str): file compression path
        control? (dict): file control

    Raises:
        FrictionlessException: if there is a metadata validation error

    """

    def __init__(
        self,
        source,
        *,
        scheme=None,
        format=None,
        hashing=None,
        encoding=None,
        compression=None,
        compression_path=None,
        control=None,
    ):

        # Store state
        self.__loader = None

        # Create resource
        self.__resource = Resource.from_source(
            source,
            scheme=scheme,
            format=format,
            hashing=hashing,
            encoding=encoding,
            compression=compression,
            compression_path=compression_path,
            control=control,
            trusted=True,
        )

    def __enter__(self):
        if self.closed:
            self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __iter__(self):
        self.__read_raise_closed()
        return iter(self.__loader.__text_stream)

    @property
    def path(self):
        """
        Returns:
            str: file path
        """
        return self.__resource.path

    @property
    def source(self):
        """
        Returns:
            any: file source
        """
        return self.__resource.source

    @property
    def scheme(self):
        """
        Returns:
            str?: file scheme
        """
        return self.__resource.scheme

    @property
    def format(self):
        """
        Returns:
            str?: file format
        """
        return self.__resource.format

    @property
    def hashing(self):
        """
        Returns:
            str?: file hashing
        """
        return self.__resource.hashing

    @property
    def encoding(self):
        """
        Returns:
            str?: file encoding
        """
        return self.__resource.encoding

    @property
    def compression(self):
        """
        Returns:
            str?: file compression
        """
        return self.__resource.compression

    @property
    def compression_path(self):
        """
        Returns:
            str?: file compression path
        """
        return self.__resource.compression_path

    @property
    def control(self):
        """
        Returns:
            Control?: file control
        """
        return self.__resource.control

    @property
    def stats(self):
        """
        Returns:
            dict: file stats
        """
        return self.__resource.stats

    @property
    def byte_stream(self):
        """File byte stream

        The stream is available after opening the file

        Returns:
            io.ByteStream: file byte stream
        """
        if self.__loader:
            return self.__loader.byte_stream

    @property
    def text_stream(self):
        """File text stream

        The stream is available after opening the file

        Returns:
            io.TextStream: file text stream
        """
        if self.__loader:
            return self.__loader.text_stream

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("scheme", self.scheme)
        self.setdefault("format", self.format)
        self.setdefault("hashing", self.hashing)
        self.setdefault("encoding", self.encoding)
        self.setdefault("compression", self.compression)
        self.setdefault("compressionPath", self.compression_path)

    # Open/close

    def open(self):
        """Open the file as "io.open" does"""
        self.close()
        try:
            self.__resource.stats = {"hash": "", "bytes": 0, "fields": 0, "rows": 0}
            # NOTE: handle cases like Inline/SQL/etc
            self.__loader = system.create_loader(self.__resource)
            self.__loader.open()
            return self
        except Exception:
            self.close()
            raise

    def close(self):
        """Close the file as "filelike.close" does"""
        if self.__loader:
            self.__loader.close()
        self.__loader = None

    @property
    def closed(self):
        """Whether the file is closed

        Returns:
            bool: if closed
        """
        return self.__loader is None

    # Read

    def read_bytes(self):
        """Read bytes from the file

        Returns:
            bytes: file bytes
        """
        self.__read_raise_closed()
        return self.__loader.byte_stream.read1()

    def read_text(self):
        """Read bytes from the file

        Returns:
            str: file text
        """
        result = ""
        self.__read_raise_closed()
        for line in self.__loader.text_stream:
            result += line
        return result

    def __read_raise_closed(self):
        if not self.__loader:
            note = 'the file has not been opened by "file.open()"'
            raise exceptions.FrictionlessException(errors.Error(note=note))

    # Write

    def write(self, target):
        """Write the file to the target

        Parameters:
            target (str): target path
        """
        with tempfile.NamedTemporaryFile(delete=False) as file:
            shutil.copyfileobj(self.byte_stream, file)
        helpers.move_file(file.name, target)
