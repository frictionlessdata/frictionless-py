import io
import os
import json
import zipfile
from copy import deepcopy
from urllib.request import urlopen
from .metadata import Metadata
from .dialects import Dialect
from .schema import Schema
from .system import system
from .table import Table
from .file import File
from . import exceptions
from . import dialects
from . import helpers
from . import errors
from . import config


class Resource(Metadata):
    """Resource representation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Resource`

    Parameters:
        descriptor? (str|dict): report descriptor
        name? (str): package name (for machines)
        title? (str): package title (for humans)
        descriptor? (str): package descriptor
        path? (str): file path
        data? (any[][]): array or data arrays
        scheme? (str): file scheme
        format? (str): file format
        hashing? (str): file hashing
        encoding? (str): file encoding
        compression? (str): file compression
        compression_path? (str): file compression path
        dialect? (dict): table dialect
        schema? (dict): file schema
        profile? (str): resource profile
        basepath? (str): resource basepath
        trusted? (bool): don't raise on unsage paths
        package? (Package): resource package

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(
        self,
        descriptor=None,
        *,
        name=None,
        title=None,
        description=None,
        path=None,
        data=None,
        scheme=None,
        format=None,
        hashing=None,
        encoding=None,
        compression=None,
        compression_path=None,
        dialect=None,
        schema=None,
        profile=None,
        basepath=None,
        trusted=False,
        package=None,
    ):

        # Handle zip
        if helpers.is_zip_descriptor(descriptor):
            descriptor = helpers.unzip_descriptor(descriptor, "dataresource.json")

        # Set attributes
        self.setinitial("name", name)
        self.setinitial("title", title)
        self.setinitial("description", description)
        self.setinitial("path", path)
        self.setinitial("data", data)
        self.setinitial("scheme", scheme)
        self.setinitial("format", format)
        self.setinitial("hashing", hashing)
        self.setinitial("encoding", encoding)
        self.setinitial("compression", compression)
        self.setinitial("compressionPath", compression_path)
        self.setinitial("dialect", dialect)
        self.setinitial("schema", schema)
        self.setinitial("profile", profile)
        self.__basepath = basepath or helpers.detect_basepath(descriptor)
        self.__trusted = trusted
        self.__package = package
        super().__init__(descriptor)

        # Set hashing
        hashing, hash = helpers.parse_resource_hash(self.get("hash"))
        if hashing != config.DEFAULT_HASHING:
            self["hashing"] = hashing

    @Metadata.property
    def name(self):
        """
        Returns
            str: resource name
        """
        return self.get("name", "resource")

    @Metadata.property
    def title(self):
        """
        Returns
            str: resource title
        """
        return self.get("title")

    @Metadata.property
    def description(self):
        """
        Returns
            str: resource description
        """
        return self.get("description")

    # NOTE: should it be memory for inline?
    @Metadata.property
    def path(self):
        """
        Returns
            str?: resource path
        """
        return self.get("path")

    @Metadata.property
    def data(self):
        """
        Returns
            any[][]?: resource data
        """
        return self.get("data")

    # NOTE: rewrite this method
    @Metadata.property(write=False)
    def source(self):
        """
        Returns
            any: data source
        """
        path = self.path
        if self.inline:
            return self.data
        if not path:
            return []
        for path_item in path if isinstance(path, list) else [path]:
            if not self.__trusted and not helpers.is_safe_path(path_item):
                note = f'path "{path_item}" is not safe'
                raise exceptions.FrictionlessException(errors.ResourceError(note=note))
        if self.multipart:
            drop_header = False
            if path[0].endswith(".csv"):
                dialect = dialects.CsvDialect(self.get("dialect"))
                if dialect.header:
                    drop_header = True
            for index, path_item in enumerate(path):
                if not helpers.is_remote_path(path_item):
                    path[index] = os.path.join(self.basepath, path_item)
            return MultipartSource(path, drop_header=drop_header)
        if not helpers.is_remote_path(path):
            return os.path.join(self.basepath, path)
        return path

    @Metadata.property(write=False)
    def basepath(self):
        """
        Returns
            str: resource basepath
        """
        return self.__basepath

    # NOTE: move this logic to path?
    @Metadata.property(write=False)
    def fullpath(self):
        """
        Returns
            str: resource fullpath
        """
        if self.inline:
            return "memory"
        if helpers.is_remote_path(self.path):
            return self.path
        return os.path.join(self.basepath, self.path)

    @Metadata.property(write=False)
    def inline(self):
        """
        Returns
            bool: if resource is inline
        """
        return "data" in self

    # NOTE: optimize tabular/infer
    @Metadata.property(write=False)
    def tabular(self):
        """
        Returns
            bool: if resource is tabular
        """
        table = self.to_table()
        try:
            table.open()
        except Exception as exception:
            if exception.error.code == "format-error":
                return False
        except Exception:
            pass
        finally:
            table.close()
        return True

    @Metadata.property(write=False)
    def remote(self):
        """
        Returns
            bool: if resource is remote
        """
        if self.inline:
            return False
        return helpers.is_remote_path(self.path[0] if self.multipart else self.path)

    @Metadata.property(write=False)
    def multipart(self):
        """
        Returns
            bool: if resource is multipart
        """
        return bool(self.path and isinstance(self.path, list) and len(self.path) >= 2)

    @Metadata.property
    def scheme(self):
        """
        Returns
            str?: resource scheme
        """
        return self.get("scheme")

    @Metadata.property
    def format(self):
        """
        Returns
            str?: resource format
        """
        return self.get("format")

    @Metadata.property
    def hashing(self):
        """
        Returns
            str?: resource hashing
        """
        return self.get("hashing")

    @Metadata.property
    def encoding(self):
        """
        Returns
            str?: resource encoding
        """
        return self.get("encoding")

    @Metadata.property
    def compression(self):
        """
        Returns
            str?: resource compression
        """
        return self.get("compression")

    @Metadata.property
    def compression_path(self):
        """
        Returns
            str?: resource compression path
        """
        return self.get("compressionPath")

    @Metadata.property
    def stats(self):
        """
        Returns
            dict?: resource stats
        """
        stats = {}
        for name in ["hash", "bytes", "rows"]:
            value = self.get(name)
            if value is not None:
                if name == "hash":
                    value = helpers.parse_resource_hash(value)[1]
                stats[name] = value
        return stats

    @Metadata.property
    def dialect(self):
        """
        Returns
            Dialect?: resource dialect
        """
        dialect = self.get("dialect")
        if dialect is None:
            dialect = self.metadata_attach("dialect", Dialect())
        elif isinstance(dialect, str):
            if not self.__trusted and not helpers.is_safe_path(dialect):
                note = f'dialect path "{dialect}" is not safe'
                raise exceptions.FrictionlessException(errors.ResourceError(note=note))
            dialect = Dialect(os.path.join(self.basepath, dialect))
        return dialect

    @Metadata.property
    def schema(self):
        """
        Returns
            Schema: resource schema
        """
        schema = self.get("schema")
        if schema is None:
            schema = self.metadata_attach("schema", Schema())
        elif isinstance(schema, str):
            if not self.__trusted and not helpers.is_safe_path(schema):
                note = f'schema path "{schema}" is not safe'
                raise exceptions.FrictionlessException(errors.ResourceError(note=note))
            schema = Schema(os.path.join(self.basepath, schema))
        return schema

    @Metadata.property
    def profile(self):
        """
        Returns
            str?: resource profile
        """
        return self.get("profile", config.DEFAULT_RESOURCE_PROFILE)

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("profile", config.DEFAULT_RESOURCE_PROFILE)
        if isinstance(self.get("dialect"), Dialect):
            self.dialect.expand()
        if isinstance(self.get("schema"), Schema):
            self.schema.expand()

    # Infer

    # NOTE: optimize this logic/don't re-open
    def infer(self, source=None, *, only_sample=False):
        """Infer metadata

        Parameters:
            source (str|str[]): path, list of paths or glob pattern
            only_sample? (bool): infer whatever possible but only from the sample
        """
        patch = {}

        # From source
        if source:
            if isinstance(source, str):
                self.path = source
            if isinstance(source, list):
                self.data = source

        # Tabular
        if self.tabular:
            with self.to_table() as table:
                patch["profile"] = "tabular-data-resource"
                patch["name"] = self.get("name", helpers.detect_name(table.path))
                patch["scheme"] = table.scheme
                patch["format"] = table.format
                patch["hashing"] = table.hashing
                patch["encoding"] = table.encoding
                patch["compression"] = table.compression
                patch["compressionPath"] = table.compression_path
                patch["dialect"] = table.dialect
                patch["schema"] = table.schema

        # General
        else:
            with self.to_file() as file:
                patch["profile"] = "data-resource"
                patch["name"] = self.get("name", helpers.detect_name(file.path))
                patch["scheme"] = file.scheme
                patch["format"] = file.format
                patch["hashing"] = file.hashing
                patch["encoding"] = file.encoding
                patch["compression"] = file.compression
                patch["compressionPath"] = file.compression_path

        # Stats
        if not only_sample:
            stats = self.read_stats()
            patch.update(stats)
            if patch["hashing"] != config.DEFAULT_HASHING:
                patch["hash"] = ":".join([patch["hashing"], patch["hash"]])

        # Apply/expand
        self.update(patch)

    # Read

    def read_bytes(self):
        """
        Returns:
            bytes: resource bytes
        """
        byte_stream = self.read_byte_stream()
        bytes = byte_stream.read1(io.DEFAULT_BUFFER_SIZE)
        byte_stream.close()
        return bytes

    def read_byte_stream(self):
        """
        Returns:
            io.ByteStream: resource byte stream
        """
        if self.inline:
            return io.BytesIO(b"")
        file = self.to_file()
        file.open()
        return file.byte_stream

    def read_text(self):
        """
        Returns:
            str: resource text
        """
        text = ""
        text_stream = self.read_text_stream()
        for line in text_stream:
            text += line
        text_stream.close()
        return text

    def read_text_stream(self):
        """
        Returns:
            io.TextStream: resource text stream
        """
        if self.inline:
            return io.StringIO("")
        file = self.to_file()
        file.open()
        return file.text_stream

    def read_data(self):
        """
        Returns:
            any[][]: array of data arrays
        """
        data = list(self.read_data_stream())
        return data

    def read_data_stream(self):
        """
        Returns:
            gen<any[][]>: data stream
        """
        with self.to_table() as table:
            for cells in table.data_stream:
                yield cells

    def read_rows(self):
        """
        Returns
            Row[]: resource rows
        """
        rows = list(self.read_row_stream())
        return rows

    def read_row_stream(self):
        """
        Returns
            gen<Row[]>: row stream
        """
        with self.to_table() as table:
            for row in table.row_stream:
                yield row

    def read_header(self):
        """
        Returns
            Header: resource header
        """
        with self.to_table() as table:
            return table.header

    def read_sample(self):
        """
        Returns
            any[][]: resource sample
        """
        with self.to_table() as table:
            return table.sample

    # NOTE: optimize this logic/don't re-open
    def read_stats(self):
        """
        Returns
            dict: resource stats
        """

        # Tabular
        if self.tabular:
            with self.to_table() as table:
                helpers.pass_through(table.data_stream)
                return table.stats

        # General
        # NOTE: make loader.ByteStreamWithStatsHandling iterable / rebase on pass_through?
        with self.to_file() as file:
            bytes = True
            while bytes:
                bytes = file.byte_stream.read1(io.DEFAULT_BUFFER_SIZE)
            return file.stats

    def read_lookup(self):
        """
        Returns
            dict: resource lookup structure
        """
        lookup = {}
        for fk in self.schema.foreign_keys:
            source_name = fk["reference"]["resource"]
            source_key = tuple(fk["reference"]["fields"])
            if source_name != "" and not self.__package:
                continue
            source_res = self.__package.get_resource(source_name) if source_name else self
            lookup.setdefault(source_name, {})
            if source_key in lookup[source_name]:
                continue
            lookup[source_name][source_key] = set()
            if not source_res:
                continue
            with source_res.to_table(lookup=None) as table:
                for row in table.row_stream:
                    cells = tuple(row.get(field_name) for field_name in source_key)
                    if set(cells) == {None}:
                        continue
                    lookup[source_name][source_key].add(cells)
        return lookup

    # Import/Export

    @staticmethod
    def from_storage(storage, *, name):
        """Import resource from storage

        Parameters:
            storage (Storage): storage instance
            name (str): resource name
        """
        return storage.read_resource(name)

    def to_storage(self, storage, *, force=False):
        """Export resource to storage

        Parameters:
            storage (Storage): storage instance
            force (bool): overwrite existent
        """
        storage.write_resource(self, force=force)
        return storage

    @staticmethod
    def from_sql(*, name, engine, prefix="", namespace=None):
        """Import resource from SQL table

        Parameters:
            name (str): resource name
            engine (object): `sqlalchemy` engine
            prefix (str): prefix for all tables
            namespace (str): SQL scheme
        """
        return Resource.from_storage(
            system.create_storage(
                "sql", engine=engine, prefix=prefix, namespace=namespace
            ),
            name=name,
        )

    def to_sql(self, *, engine, prefix="", namespace=None, force=False):
        """Export resource to SQL table

        Parameters:
            engine (object): `sqlalchemy` engine
            prefix (str): prefix for all tables
            namespace (str): SQL scheme
            force (bool): overwrite existent
        """
        return self.to_storage(
            system.create_storage(
                "sql", engine=engine, prefix=prefix, namespace=namespace
            ),
            force=force,
        )

    @staticmethod
    def from_pandas(dataframe):
        """Import resource from Pandas dataframe

        Parameters:
            dataframe (str): padas dataframe
        """
        return Resource.from_storage(
            system.create_storage("pandas", dataframes={"name": dataframe}),
            name="name",
        )

    def to_pandas(self):
        """Export resource to Pandas dataframe

        Parameters:
            dataframes (dict): pandas dataframes
            force (bool): overwrite existent
        """
        return self.to_storage(system.create_storage("pandas"))

    def to_dict(self, expand=False):
        """Convert resource to dict

        Parameters:
            expand (bool): whether to expand
        """
        result = super().to_dict()
        if expand:
            result = type(self)(result)
            result.expand()
            result = result.to_dict()
        return result

    # NOTE: cache lookup?
    def to_table(self, **options):
        """Convert resource to Table

        Parameters:
            **options (dict): table options

        Returns:
            Table: data table
        """
        options.setdefault("source", self.source)
        options.setdefault("scheme", self.scheme)
        options.setdefault("format", self.format)
        options.setdefault("hashing", self.hashing)
        options.setdefault("encoding", self.encoding)
        options.setdefault("compression", self.compression)
        options.setdefault("compression_path", self.compression_path)
        options.setdefault("dialect", self.dialect)
        options.setdefault("schema", self.schema)
        if "lookup" not in options:
            options["lookup"] = self.read_lookup()
        return Table(**options)

    def to_file(self, **options):
        """Convert resource to File

        Parameters:
            **options (dict): file options

        Returns:
            File: data file
        """
        options.setdefault("source", self.source)
        options.setdefault("scheme", self.scheme)
        options.setdefault("format", self.format)
        options.setdefault("hashing", self.hashing)
        options.setdefault("encoding", self.encoding)
        options.setdefault("compression", self.compression)
        options.setdefault("compression_path", self.compression_path)
        return File(**options)

    # NOTE: support multipart
    def to_zip(self, target, encoder_class=None):
        """Save resource to a zip

        Parameters:
            target (str): target path

        Raises:
            FrictionlessException: on any error
        """
        try:
            with zipfile.ZipFile(target, "w") as zip:
                descriptor = self.copy()
                for resource in [self]:
                    if resource.inline:
                        continue
                    if resource.remote:
                        continue
                    if resource.multipart:
                        continue
                    if not helpers.is_safe_path(resource.path):
                        continue
                    zip.write(resource.source, resource.path)
                descriptor = json.dumps(
                    descriptor, indent=2, ensure_ascii=False, cls=encoder_class
                )
                zip.writestr("dataresource.json", descriptor)
        except (IOError, zipfile.BadZipfile, zipfile.LargeZipFile) as exception:
            error = errors.ResourceError(note=str(exception))
            raise exceptions.FrictionlessException(error) from exception

    # Metadata

    metadata_duplicate = True
    metadata_Error = errors.ResourceError
    metadata_profile = deepcopy(config.RESOURCE_PROFILE)
    metadata_profile["properties"]["dialect"] = {"type": "object"}
    metadata_profile["properties"]["schema"] = {"type": "object"}

    def metadata_process(self):

        # Dialect
        dialect = self.get("dialect")
        if not isinstance(dialect, (str, type(None), Dialect)):
            dialect = system.create_dialect(self.to_file(), descriptor=dialect)
            dict.__setitem__(self, "dialect", dialect)

        # Schema
        schema = self.get("schema")
        if not isinstance(schema, (str, type(None), Schema)):
            schema = Schema(schema)
            dict.__setitem__(self, "schema", schema)

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Dialect
        if self.dialect:
            yield from self.dialect.metadata_errors

        # Schema
        if self.schema:
            yield from self.schema.metadata_errors


# Internal


class MultipartSource:
    def __init__(self, source, *, drop_header):
        self.__source = source
        self.__drop_header = drop_header
        self.__line_stream = self.read_line_stream()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def __iter__(self):
        return self.__rows

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
        if helpers.is_remote_path(self.__source[0]):
            streams = (urlopen(chunk) for chunk in self.__source)
        else:
            streams = (io.open(chunk, "rb") for chunk in self.__source)
        for stream_number, stream in enumerate(streams, start=1):
            for line_number, line in enumerate(stream, start=1):
                if not line.endswith(b"\n"):
                    line += b"\n"
                if self.__drop_header and stream_number > 1 and line_number == 1:
                    continue
                yield line
