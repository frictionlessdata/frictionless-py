import io
import os
import json
import petl
import zipfile
import warnings
from copy import deepcopy
from importlib import import_module
from .metadata import Metadata
from .location import Location
from .controls import Control
from .dialects import Dialect
from .schema import Schema
from .system import system
from .query import Query
from . import exceptions
from . import helpers
from . import errors
from . import config


# TODO: rework path/data/location etc
# TODO: rework path/data updates syncing
# TODO: implement save/write as we have table.write
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
        control? (dict): file control
        dialect? (dict): table dialect
        query? (dict): table query
        schema? (dict): table schema
        stats? (dict): table stats
        profile? (str): resource profile
        basepath? (str): resource basepath
        onerror? (ignore|warn|raise): behaviour if there is an error
        trusted? (bool): don't raise an exception on unsafe paths
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
        control=None,
        dialect=None,
        query=None,
        schema=None,
        stats=None,
        profile=None,
        basepath=None,
        onerror="ignore",
        trusted=False,
        package=None,
    ):

        # Handle zip
        if helpers.is_zip_descriptor(descriptor):
            descriptor = helpers.unzip_descriptor(descriptor, "dataresource.json")

        # TODO: Handle stats: hash/bytes/rows

        # Set attributes
        self.setinitial("name", name)
        self.setinitial("title", title)
        self.setinitial("description", description)
        self.setinitial("profile", profile)
        self.setinitial("path", path)
        self.setinitial("data", data)
        self.setinitial("scheme", scheme)
        self.setinitial("format", format)
        self.setinitial("hashing", hashing)
        self.setinitial("encoding", encoding)
        self.setinitial("compression", compression)
        self.setinitial("compressionPath", compression_path)
        self.setinitial("control", control)
        self.setinitial("dialect", dialect)
        self.setinitial("query", query)
        self.setinitial("schema", schema)
        self.setinitial("stats", stats)
        self.__basepath = basepath or helpers.detect_basepath(descriptor)
        self.__onerror = onerror
        self.__trusted = trusted
        self.__package = package
        super().__init__(descriptor)

        # Replace deprecated "url"
        url = self.get("url")
        path = self.get("path")
        if url and not path:
            message = 'Property "url" is deprecated. Please use "path" instead.'
            warnings.warn(message, UserWarning)
            self["path"] = self.pop("url")

    def __setattr__(self, name, value):
        if name == "basepath":
            self.__basepath = value
        elif name == "onerror":
            self.__onerror = value
        elif name == "trusted":
            self.__trusted = value
        elif name == "package":
            self.__package = value
        else:
            return super().__setattr__(name, value)
        self.metadata_process()

    def __iter__(self):
        yield from self.read_row_stream() if self.tabular else []

    @Metadata.property(write=False)
    def source(self):
        """
        Returns
            any: data source
        """
        return self.__location.source

    @Metadata.property
    def name(self):
        """
        Returns
            str: resource name
        """
        return self.get("name", self.__location.name)

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

    @Metadata.property
    def profile(self):
        """
        Returns
            str?: resource profile
        """
        return self.get("profile", config.DEFAULT_RESOURCE_PROFILE)

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

    @Metadata.property
    def scheme(self):
        """
        Returns
            str?: resource scheme
        """
        return self.get("scheme", self.__location.scheme).lower()

    @Metadata.property
    def format(self):
        """
        Returns
            str?: resource format
        """
        return self.get("format", self.__location.format).lower()

    @Metadata.property
    def hashing(self):
        """
        Returns
            str?: resource hashing
        """
        return self.get("hashing", config.DEFAULT_HASHING).lower()

    @Metadata.property
    def encoding(self):
        """
        Returns
            str?: resource encoding
        """
        return self.get("encoding", config.DEFAULT_ENCODING).lower()

    @Metadata.property
    def compression(self):
        """
        Returns
            str?: resource compression
        """
        return self.get("compression", self.__location.compression).lower()

    @Metadata.property
    def compression_path(self):
        """
        Returns
            str?: resource compression path
        """
        return self.get("compressionPath", self.__location.compression_path)

    @Metadata.property
    def control(self):
        """
        Returns
            Control?: resource control
        """
        control = self.get("control")
        if control is None:
            control = system.create_control(self, descriptor=control)
            control = self.metadata_attach("control", control)
        elif isinstance(control, str):
            control = os.path.join(self.basepath, control)
            control = system.create_control(self, descriptor=control)
            control = self.metadata_attach("control", control)
        return control

    @Metadata.property
    def dialect(self):
        """
        Returns
            Dialect?: resource dialect
        """
        dialect = self.get("dialect")
        if dialect is None:
            dialect = system.create_dialect(self, descriptor=dialect)
            dialect = self.metadata_attach("dialect", dialect)
        elif isinstance(dialect, str):
            dialect = os.path.join(self.basepath, dialect)
            dialect = system.create_control(self, descriptor=dialect)
            dialect = self.metadata_attach("dialect", dialect)
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
            query = self.metadata_attach("query", query)
        elif isinstance(query, str):
            query = Query(os.path.join(self.basepath, query))
            query = self.metadata_attach("query", query)
        return query

    @Metadata.property
    def schema(self):
        """
        Returns
            Schema: resource schema
        """
        schema = self.get("schema")
        if schema is None:
            schema = Schema()
            schema = self.metadata_attach("schema", schema)
        elif isinstance(schema, str):
            schema = Schema(os.path.join(self.basepath, schema))
            schema = self.metadata_attach("schema", schema)
        return schema

    @Metadata.property
    def stats(self):
        """
        Returns
            dict?: resource stats
        """
        stats = {"hash": "", "bytes": 0, "fields": 0, "rows": 0}
        return self.metadata_attach("stats", self.get("stats", stats))

    @Metadata.property(write=False)
    def basepath(self):
        """
        Returns
            str: resource basepath
        """
        return self.__basepath

    @Metadata.property(write=False)
    def fullpath(self):
        """
        Returns
            str: resource fullpath
        """
        if self.inline:
            return "memory"
        if self.multipart:
            return "multipart"
        return self.source

    @property
    def onerror(self):
        """
        Returns:
            ignore|warn|raise: on error bahaviour
        """
        assert self.__onerror in ["ignore", "warn", "raise"]
        return self.__onerror

    @property
    def trusted(self):
        """
        Returns:
            bool: don't raise an exception on unsafe paths
        """
        return self.__trusted

    @property
    def package(self):
        """
        Returns:
            Package?: parent package
        """
        return self.__package

    @Metadata.property(write=False)
    def inline(self):
        """
        Returns
            bool: if resource is inline
        """
        return self.__location.inline

    @Metadata.property(write=False)
    def multipart(self):
        """
        Returns
            bool: if resource is multipart
        """
        return self.__location.multipart

    @Metadata.property(write=False)
    def remote(self):
        """
        Returns
            bool: if resource is remote
        """
        return self.__location.remote

    @Metadata.property(write=False)
    def tabular(self):
        """
        Returns
            bool: if resource is tabular
        """
        try:
            system.create_parser(self)
            return True
        except Exception:
            return False

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("profile", config.DEFAULT_RESOURCE_PROFILE)
        if isinstance(self.get("control"), Control):
            self.control.expand()
        if isinstance(self.get("dialect"), Dialect):
            self.dialect.expand()
        if isinstance(self.get("query"), Query):
            self.query.expand()
        if isinstance(self.get("schema"), Schema):
            self.schema.expand()

    # Infer

    # TODO: use stats=True instead of only_sample?
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
                patch["name"] = self.name
                patch["profile"] = "tabular-data-resource"
                patch["scheme"] = table.scheme
                patch["format"] = table.format
                patch["hashing"] = table.hashing
                patch["encoding"] = table.encoding
                patch["compression"] = table.compression
                patch["compressionPath"] = table.compression_path
                patch["compressionPath"] = table.compression_path
                patch["control"] = table.control
                patch["dialect"] = table.dialect
                patch["query"] = table.query
                patch["schema"] = table.schema

        # General
        else:
            with self.to_file() as file:
                patch["name"] = self.name
                patch["profile"] = "data-resource"
                patch["scheme"] = file.scheme
                patch["format"] = file.format
                patch["hashing"] = file.hashing
                patch["encoding"] = file.encoding
                patch["compression"] = file.compression
                patch["compressionPath"] = file.compression_path
                patch["control"] = file.control

        # Stats
        if not only_sample:
            patch["stats"] = self.read_stats()

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
    def from_source(source, **options):
        if source is None:
            return Resource(data=[], **options)
        elif isinstance(source, str):
            return Resource(path=source, **options)
        elif isinstance(source, list) and source and isinstance(source[0], str):
            return Resource(path=source, **options)
        return Resource(data=source, **options)

    @staticmethod
    def from_petl(storage, *, view, **options):
        return Resource(data=view, **options)

    @staticmethod
    def from_storage(storage, *, name):
        """Import resource from storage

        Parameters:
            storage (Storage): storage instance
            name (str): resource name
        """
        return storage.read_resource(name)

    @staticmethod
    def from_ckan(*, base_url, resource_id, api_key=None):
        """Import resource from CKAN

        Parameters:
            base_url (str): (required) URL for CKAN instance (e.g: https://demo.ckan.org/ )
            resource_id (str): (required) ID of resource to fetch
            api_key (str): (optional) Your CKAN API key
        """
        return Resource.from_storage(
            system.create_storage(
                "ckan_datastore",
                base_url=base_url,
                api_key=api_key,
            ),
            name=resource_id,
        )

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

    @staticmethod
    def from_spss(*, name, basepath):
        """Import resource from SPSS file

        Parameters:
            name (str): resource name
            basepath (str): SPSS dir path
        """
        return Resource.from_storage(
            system.create_storage("spss", basepath=basepath),
            name=name,
        )

    @staticmethod
    def from_bigquery(*, name, service, project, dataset, prefix=""):
        """Import resource from BigQuery table

        Parameters:
            name (str): resource name
            service (object): BigQuery `Service` object
            project (str): BigQuery project name
            dataset (str): BigQuery dataset name
            prefix? (str): prefix for all names
        """
        return Resource.from_storage(
            system.create_storage(
                "bigquery",
                service=service,
                project=project,
                dataset=dataset,
                prefix=prefix,
            ),
            name=name,
        )

    def to_copy(self):
        """Create a copy of the resource"""
        descriptor = self.to_dict()
        # Data can be not serializable (generators/functions)
        data = descriptor.pop("data", None)
        return Resource(
            descriptor,
            data=data,
            basepath=self.__basepath,
            onerror=self.__onerror,
            trusted=self.__trusted,
            package=self.__package,
        )

    # NOTE: cache lookup?
    def to_table(self, **options):
        """Convert resource to Table

        Parameters:
            **options (dict): table options

        Returns:
            Table: data table
        """
        module = import_module("frictionless.table")
        options.setdefault("source", self.source)
        options.setdefault("scheme", self.scheme)
        options.setdefault("format", self.format)
        options.setdefault("hashing", self.hashing)
        options.setdefault("encoding", self.encoding)
        options.setdefault("compression", self.compression)
        options.setdefault("compression_path", self.compression_path)
        options.setdefault("control", self.control)
        options.setdefault("dialect", self.dialect)
        options.setdefault("query", self.query)
        options.setdefault("schema", self.schema)
        options.setdefault("onerror", self.__onerror)
        if "lookup" not in options:
            options["lookup"] = self.read_lookup()
        return module.Table(**options)

    def to_file(self, **options):
        """Convert resource to File

        Parameters:
            **options (dict): file options

        Returns:
            File: data file
        """
        module = import_module("frictionless.file")
        options.setdefault("source", self.source)
        options.setdefault("scheme", self.scheme)
        options.setdefault("format", self.format)
        options.setdefault("hashing", self.hashing)
        options.setdefault("encoding", self.encoding)
        options.setdefault("compression", self.compression)
        options.setdefault("compression_path", self.compression_path)
        options.setdefault("control", self.control)
        return module.File(**options)

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

    def to_petl(self, *, normalize=False):
        resource = self

        # Define view
        class ResourceView(petl.Table):
            def __iter__(self):
                stream = (
                    map(lambda row: row.to_list(), resource.read_row_stream())
                    if normalize
                    else resource.read_data_stream()
                )
                yield resource.schema.field_names
                yield from stream

        return ResourceView()

    def to_storage(self, storage, *, force=False):
        """Export resource to storage

        Parameters:
            storage (Storage): storage instance
            force (bool): overwrite existent
        """
        storage.write_resource(self.to_copy(), force=force)
        return storage

    def to_ckan(self, *, base_url, dataset_id=None, api_key=None, force=False):
        """Export resource to CKAN

        Parameters:
            base_url (str): (required) URL for CKAN instance (e.g: https://demo.ckan.org/ )
            dataset_id (str): (optional) ID or slug of dataset this resource belongs to
            api_key (str): (optional) Your CKAN API key
            force (bool): (optional) overwrite existing data
        """
        return self.to_storage(
            system.create_storage(
                "ckan_datastore",
                base_url=base_url,
                dataset_id=dataset_id,
                api_key=api_key,
            ),
            force=force,
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

    def to_pandas(self):
        """Export resource to Pandas dataframe

        Parameters:
            dataframes (dict): pandas dataframes
            force (bool): overwrite existent
        """
        return self.to_storage(system.create_storage("pandas"))

    def to_spss(self, *, basepath, force=False):
        """Export resource to SPSS file

        Parameters:
            basepath (str): SPSS dir path
            force (bool): overwrite existent
        """
        return self.to_storage(
            system.create_storage("spss", basepath=basepath), force=force
        )

    def to_bigquery(self, *, service, project, dataset, prefix="", force=False):
        """Export resource to Bigquery table

        Parameters:
            service (object): BigQuery `Service` object
            project (str): BigQuery project name
            dataset (str): BigQuery dataset name
            prefix? (str): prefix for all names
            force (bool): overwrite existent
        """
        return self.to_storage(
            system.create_storage(
                "bigquery",
                service=service,
                project=project,
                dataset=dataset,
                prefix=prefix,
            ),
            force=force,
        )

    # Metadata

    metadata_duplicate = True
    metadata_Error = errors.ResourceError
    metadata_profile = deepcopy(config.RESOURCE_PROFILE)
    metadata_profile["properties"]["dialect"] = {"type": "object"}
    metadata_profile["properties"]["schema"] = {"type": "object"}

    def metadata_process(self):

        # Location
        self.__location = Location(self)

        # Control
        control = self.get("control")
        if not isinstance(control, (str, type(None))):
            control = system.create_control(self, descriptor=control)
            dict.__setitem__(self, "control", control)

        # Dialect
        dialect = self.get("dialect")
        if not isinstance(dialect, (str, type(None))):
            dialect = system.create_dialect(self, descriptor=dialect)
            dict.__setitem__(self, "dialect", dialect)

        # Query
        query = self.get("query")
        if not isinstance(query, (str, type(None), Query)):
            query = Query(query)
            dict.__setitem__(self, "query", query)

        # Schema
        schema = self.get("schema")
        if not isinstance(schema, (str, type(None), Schema)):
            schema = Schema(schema)
            dict.__setitem__(self, "schema", schema)

        # Security
        if not self.trusted:
            for name in ["path", "control", "dialect", "schema"]:
                path = self.get(name)
                if not isinstance(path, (str, list)):
                    continue
                path = path if isinstance(path, list) else [path]
                if not all(helpers.is_safe_path(chunk) for chunk in path):
                    note = f'path "{path}" is not safe'
                    error = errors.ResourceError(note=note)
                    raise exceptions.FrictionlessException(error)

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Dialect
        if self.dialect:
            yield from self.dialect.metadata_errors

        # Schema
        if self.schema:
            yield from self.schema.metadata_errors
