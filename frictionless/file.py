import os
import shutil
import tempfile
from .query import Query
from .metadata import Metadata
from .system import system
from . import exceptions
from . import helpers
from . import errors
from . import config


class File(Metadata):
    """File representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import File`

    Under the hood, File uses available loaders so it can open from local, remote,
    and any other supported schemes. The File class inherits from the Metadata class
    all the metadata's functionality

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
        dialect? (dict): table dialect
        query? (dict): table query
        newline? (str): python newline e.g. '\n',
        stats? ({hash: str, bytes: int, rows: int}): stats object

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
        dialect=None,
        query=None,
        newline=None,
        stats=None,
    ):

        # Set attributes
        self.setinitial("source", source)
        self.setinitial("scheme", scheme)
        self.setinitial("format", format)
        self.setinitial("hashing", hashing)
        self.setinitial("encoding", encoding)
        self.setinitial("compression", compression)
        self.setinitial("compressionPath", compression_path)
        self.setinitial("control", control)
        self.setinitial("dialect", dialect)
        self.setinitial("query", query)
        self.setinitial("newline", newline)
        self.setinitial("stats", stats)
        self.__loader = None

        # Detect attributes
        detect = helpers.detect_source_scheme_and_format(source)
        self.__detected_compression = config.DEFAULT_COMPRESSION
        self.__detected_compression_path = config.DEFAULT_COMPRESSION_PATH
        if detect[1] in config.COMPRESSION_FORMATS:
            self.__detected_compression = detect[1]
            source = source[: -len(detect[1]) - 1]
            if compression_path:
                source = os.path.join(source, compression_path)
            detect = helpers.detect_source_scheme_and_format(source)
        self.__detected_scheme = detect[0] or config.DEFAULT_SCHEME
        self.__detected_format = detect[1] or config.DEFAULT_FORMAT

        # Initialize file
        super().__init__()

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
        return self.source if isinstance(self.source, str) else "memory"

    @Metadata.property
    def source(self):
        """
        Returns:
            any: file source
        """
        return self.get("source")

    @Metadata.property
    def scheme(self):
        """
        Returns:
            str?: file scheme
        """
        return self.get("scheme", self.__detected_scheme)

    @Metadata.property
    def format(self):
        """
        Returns:
            str?: file format
        """
        return self.get("format", self.__detected_format)

    @Metadata.property
    def hashing(self):
        """
        Returns:
            str?: file hashing
        """
        return self.get("hashing", config.DEFAULT_HASHING)

    @Metadata.property
    def encoding(self):
        """
        Returns:
            str?: file encoding
        """
        return self.get("encoding", config.DEFAULT_ENCODING)

    @Metadata.property
    def compression(self):
        """
        Returns:
            str?: file compression
        """
        return self.get("compression", self.__detected_compression)

    @Metadata.property
    def compression_path(self):
        """
        Returns:
            str?: file compression path
        """
        return self.get("compressionPath", self.__detected_compression_path)

    @Metadata.property
    def control(self):
        """
        Returns:
            Control?: file control
        """
        control = self.get("control")
        if control is None:
            control = system.create_control(self, descriptor=control)
            return self.metadata_attach("control", control)
        return control

    @Metadata.property
    def dialect(self):
        """
        Returns:
            Dialect?: table dialect
        """
        dialect = self.get("dialect")
        if dialect is None:
            dialect = system.create_dialect(self, descriptor=dialect)
            return self.metadata_attach("dialect", dialect)
        return dialect

    @Metadata.property
    def query(self):
        """
        Returns:
            Query?: table query
        """
        query = self.get("query")
        if query is None:
            query = Query()
            return self.metadata_attach("query", query)
        return query

    @Metadata.property
    def newline(self):
        """
        Returns:
            str?: file newline
        """
        return self.get("newline")

    @Metadata.property
    def stats(self):
        """
        Returns:
            dict: file stats
        """
        return self.get("stats")

    @Metadata.property(cache=False)
    def byte_stream(self):
        """File byte stream

        The stream is available after opening the file

        Returns:
            io.ByteStream: file byte stream
        """
        if self.__loader:
            return self.__loader.byte_stream

    @Metadata.property(cache=False)
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
            self.stats = {"hash": "", "bytes": 0, "rows": 0}
            # NOTE: handle cases like Inline/SQL/etc
            self.__loader = system.create_loader(self)
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

    # Metadata

    metadata_strict = True
    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["source"],
        "properties": {
            "source": {},
            "scheme": {"type": "string"},
            "format": {"type": "string"},
            "hashing": {"type": "string"},
            "encoding": {"type": "string"},
            "compression": {"type": "string"},
            "compressionPath": {"type": "string"},
            "contorl": {"type": "object"},
            "dialect": {"type": "object"},
            "query": {"type": "object"},
            "newline": {"type": "string"},
            "stats": {
                "type": "object",
                "required": ["hash", "bytes", "rows"],
                "properties": {
                    "hash": {"type": "string"},
                    "bytes": {"type": "number"},
                    "rows": {"type": "number"},
                },
            },
        },
    }

    def metadata_process(self):
        super().metadata_process()

        # Control
        control = self.get("control")
        if control is not None:
            control = system.create_control(self, descriptor=control)
            dict.__setitem__(self, "control", control)

        # Dialect
        dialect = self.get("dialect")
        if dialect is not None:
            dialect = system.create_dialect(self, descriptor=dialect)
            dict.__setitem__(self, "dialect", dialect)

        # Query
        query = self.get("query")
        if query is not None:
            query = Query(query)
            dict.__setitem__(self, "query", query)
