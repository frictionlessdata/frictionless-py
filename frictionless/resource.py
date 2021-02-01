import os
import json
import petl
import warnings
from pathlib import Path
from copy import deepcopy
from itertools import zip_longest, chain
from .exception import FrictionlessException
from .detector import Detector
from .metadata import Metadata
from .control import Control
from .dialect import Dialect
from .layout import Layout
from .schema import Schema
from .header import Header
from .system import system
from .row import Row
from . import helpers
from . import errors
from . import config


class Resource(Metadata):
    """Resource representation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Resource`

    This class is one of the cornerstones of of Frictionless framework.
    It loads a data source, and allows you to stream its parsed contents.
    At the same time, it's a metadata class data description.

    ```python
    with Resource("data/table.csv") as resource:
        resource.header == ["id", "name"]
        resource.read_rows() == [
            {'id': 1, 'name': 'english'},
            {'id': 2, 'name': '中国人'},
        ]
    ```

    Parameters:

        source (any): Source of the resource; can be in various forms.
            Usually, it's a string as `<scheme>://path/to/file.<format>`.
            It also can be, for example, an array of data arrays/dictionaries.
            Or it can be a resource descriptor dict or path.

        descriptor (dict|str): A resource descriptor provided explicitly.
            Keyword arguments will patch this descriptor if provided.

        name? (str): A Resource name according to the specs.
            It should be a slugified name of the resource.

        title? (str): A Resource title according to the specs
           It should a human-oriented title of the resource.

        description? (str): A Resource description according to the specs
           It should a human-oriented description of the resource.

        mediatype? (str): A mediatype/mimetype of the resource e.g. “text/csv”,
            or “application/vnd.ms-excel”.  Mediatypes are maintained by the
            Internet Assigned Numbers Authority (IANA) in a media type registry.

        licenses? (dict[]): The license(s) under which the resource is provided.
            If omitted it's considered the same as the package's licenses.

        sources? (dict[]): The raw sources for this data resource.
            It MUST be an array of Source objects.
            Each Source object MUST have a title and
            MAY have path and/or email properties.

        profile? (str): A string identifying the profile of this descriptor.
            For example, `tabular-data-resource`.

        scheme? (str): Scheme for loading the file (file, http, ...).
            If not set, it'll be inferred from `source`.

        format? (str): File source's format (csv, xls, ...).
            If not set, it'll be inferred from `source`.

        hashing? (str): An algorithm to hash data.
            It defaults to 'md5'.

        encoding? (str): Source encoding.
            If not set, it'll be inferred from `source`.

        innerpath? (str): A path within the compressed file.
            It defaults to the first file in the archive.

        compression? (str): Source file compression (zip, ...).
            If not set, it'll be inferred from `source`.

        control? (dict|Control): File control.
            For more information, please check the Control documentation.

        dialect? (dict|Dialect): Table dialect.
            For more information, please check the Dialect documentation.

        layout? (dict|Layout): Table layout.
            For more information, please check the Layout documentation.

        schema? (dict|Schema): Table schema.
            For more information, please check the Schema documentation.

        stats? (dict): File/table stats.
            A dict with the following possible properties: hash, bytes, fields, rows.

        basepath? (str): A basepath of the resource
            The fullpath of the resource is joined `basepath` and /path`

        detector? (Detector): File/table detector.
            For more information, please check the Detector documentation.

        onerror? (ignore|warn|raise): Behaviour if there is an error.
            It defaults to 'ignore'. The default mode will ignore all errors
            on resource level and they should be handled by the user
            being available in Header and Row objects.

        trusted? (bool): Don't raise an exception on unsafe paths.
            A path provided as a part of the descriptor considered unsafe
            if there are path traversing or the path is absolute.
            A path provided as `source` or `path` is alway trusted.

        nolookup? (bool): Don't create a lookup table.
            A lookup table can be required by foreign keys.

        package? (Package): A owning this resource package.
            It's actual if the resource is part of some data package.

    Raises:
        FrictionlessException: raise any error that occurs during the process
    """

    def __init__(
        self,
        source=None,
        *,
        descriptor=None,
        # Spec
        name=None,
        title=None,
        description=None,
        mediatype=None,
        licenses=None,
        sources=None,
        profile=None,
        path=None,
        data=None,
        scheme=None,
        format=None,
        hashing=None,
        encoding=None,
        innerpath=None,
        compression=None,
        control=None,
        dialect=None,
        layout=None,
        schema=None,
        stats=None,
        # Extra
        basepath="",
        detector=None,
        onerror="ignore",
        trusted=False,
        nolookup=False,
        package=None,
    ):

        # Handle source
        if source is not None:
            file = system.create_file(source, basepath=basepath)
            if file.type == "table":
                if path is None:
                    path = file.path
                if data is None:
                    data = file.data
            elif descriptor is None:
                descriptor = source

        # Handle pathlib
        if isinstance(descriptor, Path):
            descriptor = str(descriptor)

        # Handle trusted
        if descriptor is None:
            trusted = True

        # Store state
        self.__loader = None
        self.__parser = None
        self.__sample = None
        self.__fragment = None
        self.__labels = None
        self.__header = None
        self.__lookup = None
        self.__byte_stream = None
        self.__text_stream = None
        self.__list_stream = None
        self.__row_stream = None
        self.__row_number = None
        self.__row_position = None
        self.__field_positions = None
        self.__fragment_positions = None

        # Store extra
        self.__basepath = basepath or helpers.parse_basepath(descriptor)
        self.__detector = detector or Detector()
        self.__onerror = onerror
        self.__trusted = trusted
        self.__nolookup = nolookup
        self.__package = package

        # Set specs
        self.setinitial("name", name)
        self.setinitial("title", title)
        self.setinitial("description", description)
        self.setinitial("mediatype", mediatype)
        self.setinitial("licenses", licenses)
        self.setinitial("sources", sources)
        self.setinitial("profile", profile)
        self.setinitial("path", path)
        self.setinitial("data", data)
        self.setinitial("scheme", scheme)
        self.setinitial("format", format)
        self.setinitial("hashing", hashing)
        self.setinitial("encoding", encoding)
        self.setinitial("compression", compression)
        self.setinitial("innerpath", innerpath)
        self.setinitial("control", control)
        self.setinitial("dialect", dialect)
        self.setinitial("layout", layout)
        self.setinitial("schema", schema)
        self.setinitial("stats", stats)
        super().__init__(descriptor)

        # NOTE: it will not work if dialect is a path
        # Handle official dialect.header
        dialect = self.get("dialect")
        if isinstance(dialect, dict):
            header = dialect.pop("header", None)
            if header is False:
                self.setdefault("layout", {})
                self["layout"]["header"] = False

        # Handle official hash/bytes/rows
        for name in ["hash", "bytes", "rows"]:
            value = self.pop(name, None)
            if value:
                if name == "hash":
                    hashing, value = helpers.parse_resource_hash(value)
                    if hashing != config.DEFAULT_HASHING:
                        self["hashing"] = hashing
                self.setdefault("stats", {})
                self["stats"][name] = value

        # Handle deprecated url
        url = self.get("url")
        path = self.get("path")
        if url and not path:
            message = 'Property "url" is deprecated. Please use "path" instead.'
            warnings.warn(message, UserWarning)
            self["path"] = self.pop("url")

        # Handle deprecated compression
        compression = self.get("compression")
        if compression == "no":
            message = 'Compression "no" is deprecated. Please use "" compression.'
            warnings.warn(message, UserWarning)
            self["compression"] = ""

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

    def __enter__(self):
        if self.closed:
            self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __iter__(self):
        self.__read_raise_closed()
        yield from self.__row_stream

    @Metadata.property
    def name(self):
        """
        Returns
            str: resource name
        """
        return self.get("name", self.__file.name)

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
    def mediatype(self):
        """
        Returns
            str: resource mediatype
        """
        return self.get("mediatype")

    @Metadata.property
    def licenses(self):
        """
        Returns
            dict[]: resource licenses
        """
        return self.get("licenses")

    @Metadata.property
    def sources(self):
        """
        Returns
            dict[]: resource sources
        """
        return self.get("sources")

    @Metadata.property
    def profile(self):
        """
        Returns
            str?: resource profile
        """
        default = config.DEFAULT_RESOURCE_PROFILE
        if not self.closed and self.tabular:
            default = "tabular-data-resource"
        return self.get("profile", default)

    @Metadata.property
    def path(self):
        """
        Returns
            str?: resource path
        """
        return self.get("path", self.__file.path)

    @Metadata.property
    def data(self):
        """
        Returns
            any[][]?: resource data
        """
        return self.get("data", self.__file.data)

    @Metadata.property
    def scheme(self):
        """
        Returns
            str?: resource scheme
        """
        return self.get("scheme", self.__file.scheme).lower()

    @Metadata.property
    def format(self):
        """
        Returns
            str?: resource format
        """
        return self.get("format", self.__file.format).lower()

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
    def innerpath(self):
        """
        Returns
            str?: resource compression path
        """
        return self.get("innerpath", self.__file.innerpath)

    @Metadata.property
    def compression(self):
        """
        Returns
            str?: resource compression
        """
        return self.get("compression", self.__file.compression).lower()

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
    def layout(self):
        """
        Returns:
            Layout?: table layout
        """
        layout = self.get("layout")
        if layout is None:
            layout = Layout()
            layout = self.metadata_attach("layout", layout)
        elif isinstance(layout, str):
            layout = Layout(os.path.join(self.basepath, layout))
            layout = self.metadata_attach("layout", layout)
        return layout

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

    # TODO: implement
    @property
    def buffer(self):
        pass

    @property
    def sample(self):
        """Table's lists used as sample.

        These sample rows are used internally to infer characteristics of the
        source file (e.g. schema, ...).

        Returns:
            list[]?: table sample
        """
        return self.__sample

    @property
    def fragment(self):
        """Table's lists used as fragment.

        These fragment rows are used internally to infer characteristics of the
        source file (e.g. schema, ...).

        Returns:
            list[]?: table fragment
        """
        return self.__fragment

    @property
    def labels(self):
        """
        Returns:
            str[]?: table labels
        """
        return self.__labels

    @property
    def header(self):
        """
        Returns:
            str[]?: table header
        """
        return self.__header

    @property
    def lookup(self):
        """
        Returns:
            any?: table lookup
        """
        return self.__lookup

    @Metadata.property
    def stats(self):
        """
        Returns
            dict?: resource stats
        """
        stats = {"hash": "", "bytes": 0, "fields": 0, "rows": 0}
        return self.metadata_attach("stats", self.get("stats", stats))

    @Metadata.property(cache=False, write=False)
    def basepath(self):
        """
        Returns
            str: resource basepath
        """
        return self.__file.basepath

    @Metadata.property(cache=False, write=False)
    def fullpath(self):
        """
        Returns
            str: resource fullpath
        """
        return self.__file.fullpath

    @Metadata.property(cache=False, write=False)
    def detector(self):
        """
        Returns
            str: resource detector
        """
        return self.__detector

    @Metadata.property(cache=False, write=False)
    def onerror(self):
        """
        Returns:
            ignore|warn|raise: on error bahaviour
        """
        return self.__onerror

    @Metadata.property(cache=False, write=False)
    def trusted(self):
        """
        Returns:
            bool: don't raise an exception on unsafe paths
        """
        return self.__trusted

    @Metadata.property(cache=False, write=False)
    def package(self):
        """
        Returns:
            Package?: parent package
        """
        return self.__package

    @Metadata.property(write=False)
    def memory(self):
        """
        Returns
            bool: if resource is memory
        """
        return self.__file.memory

    @Metadata.property(write=False)
    def remote(self):
        """
        Returns
            bool: if resource is remote
        """
        return self.__file.remote

    @Metadata.property(write=False)
    def multipart(self):
        """
        Returns
            bool: if resource is multipart
        """
        return self.__file.multipart

    @Metadata.property(write=False)
    def tabular(self):
        """
        Returns
            bool: if resource is tabular
        """
        if not self.closed:
            return bool(self.__parser)
        else:
            try:
                system.create_parser(self)
                return True
            except Exception:
                return False

    @property
    def byte_stream(self):
        """Byte stream in form of a generator

        Yields:
            gen<bytes>?: byte stream
        """
        return self.__byte_stream

    @property
    def text_stream(self):
        """Text stream in form of a generator

        Yields:
            gen<str[]>?: text stream
        """
        return self.__text_stream

    @property
    def list_stream(self):
        """List stream in form of a generator

        Yields:
            gen<any[][]>?: list stream
        """
        return self.__list_stream

    @property
    def row_stream(self):
        """Row stream in form of a generator of Row objects

        Yields:
            gen<Row[]>?: row stream
        """
        return self.__row_stream

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("profile", config.DEFAULT_RESOURCE_PROFILE)
        if isinstance(self.get("control"), Control):
            self.control.expand()
        if isinstance(self.get("dialect"), Dialect):
            self.dialect.expand()
        if isinstance(self.get("layout"), Layout):
            self.layout.expand()
        if isinstance(self.get("schema"), Schema):
            self.schema.expand()

    # Infer

    def infer(self, *, stats=False):
        """Infer metadata

        Parameters:
            stats? (bool): stream file completely and infer stats
        """
        current_stats = self.get("stats")
        with helpers.ensure_open(self):
            stream = self.__row_stream if self.tabular else self.__text_stream
            if stats:
                helpers.pass_through(stream)
            # TODO: move this code to open for consistencly between below and schema/etc?
            self["name"] = self.name
            self["profile"] = self.profile
            self["scheme"] = self.scheme
            self["format"] = self.format
            self["hashing"] = self.hashing
            self["encoding"] = self.encoding
            # TODO: review this code
            if self.innerpath:
                self["innerpath"] = self.innerpath
            if self.compression:
                self["compression"] = self.compression
            if self.control:
                self["control"] = self.control
            if self.dialect:
                self["dialect"] = self.dialect
            if self.layout:
                self["layout"] = self.layout
            if self.schema:
                self["schema"] = self.schema
            # TODO: infer mediatype (needed parser support)?
            # TODO: review it's a hack for checksum validation
            if not stats:
                if current_stats:
                    self["stats"] = current_stats
                else:
                    self.pop("stats")

    # Open/Close

    def open(self):
        """Open the resource as "io.open" does

        Raises:
            FrictionlessException: any exception that occurs
        """
        self.close()

        # Table
        try:
            # TODO: is it the right place for it?
            if self.layout.metadata_errors:
                error = self.layout.metadata_errors[0]
                raise FrictionlessException(error)
            self["stats"] = {"hash": "", "bytes": 0, "fields": 0, "rows": 0}
            self.__parser = system.create_parser(self)
            self.__parser.open()
            # TODO: make below lazy?
            self.__read_infer_sample()
            self.__header = self.__read_header()
            if not self.__nolookup:
                self.__lookup = self.__read_prepare_lookup()
            if self.__parser.loader:
                self.__byte_stream = self.__parser.loader.byte_stream
            if self.__parser.loader:
                self.__text_stream = self.__parser.loader.text_stream
            self.__list_stream = self.__read_list_stream()
            self.__row_stream = self.__read_row_stream()
            self.__row_number = 0
            self.__row_position = 0
            return self

        # File
        except FrictionlessException as exception:
            if exception.error.code != "format-error":
                self.close()
                raise
            self.__loader = system.create_loader(self)
            self.__loader.open()
            self.__byte_stream = self.__loader.byte_stream
            self.__text_stream = self.__loader.text_stream
            return self

        # Error
        except Exception:
            self.close()
            raise

    def close(self):
        """Close the table as "filelike.close" does"""
        if self.__loader:
            self.__loader.close()
            self.__loader = None
        if self.__parser:
            self.__parser.close()
            self.__parser = None

    @property
    def closed(self):
        """Whether the table is closed

        Returns:
            bool: if closed
        """
        return self.__parser is None

    # Read

    def read_bytes(self, *, size=None):
        """Read bytes into memory

        Returns:
            any[][]: resource bytes
        """
        # TODO: rework when there is proper sample caching
        if self.memory:
            return b""
        self["stats"] = {"hash": "", "bytes": 0, "fields": 0, "rows": 0}
        with system.create_loader(self) as loader:
            return loader.byte_stream.read1(size)

    def read_text(self, *, size=None):
        """Read text into memory

        Returns:
            str: resource text
        """
        # TODO: rework when there is proper sample caching
        if self.memory:
            return ""
        self["stats"] = {"hash": "", "bytes": 0, "fields": 0, "rows": 0}
        with system.create_loader(self) as loader:
            result = ""
            for line in loader.text_stream:
                result += line
                if size and len(result) >= size:
                    # TODO: it's not good; can we read using text_stream.read()?
                    result = result[:size]
                    break
            return result

    def read_data(self, *, size=None):
        """Read data into memory

        Returns:
            any: resource data
        """
        if self.data:
            return self.data
        text = self.read_text()
        data = json.loads(text)
        return data

    def read_lists(self, *, size=None):
        """Read lists into memory

        Returns:
            any[][]: table lists
        """
        with helpers.ensure_open(self):
            lists = []
            for cells in self.__list_stream:
                lists.append(cells)
                if size and len(lists) >= size:
                    break
            return lists

    def read_rows(self, *, size=None):
        """Read rows into memory

        Returns:
            Row[]: table rows
        """
        with helpers.ensure_open(self):
            rows = []
            for row in self.__row_stream:
                rows.append(row)
                if size and len(rows) >= size:
                    break
            return rows

    def __read_row_stream(self):
        schema = self.schema

        # Create field info
        # This structure is optimized and detached version of schema.fields
        # We create all data structures in-advance to share them between rows
        field_number = 0
        field_info = {"names": [], "objects": [], "positions": [], "mapping": {}}
        for field, field_position in zip_longest(schema.fields, self.__field_positions):
            if field is None:
                break
            field_number += 1
            field_info["names"].append(field.name)
            field_info["objects"].append(field.to_copy())
            field_info["mapping"][field.name] = (field, field_number, field_position)
            if field_position is not None:
                field_info["positions"].append(field_position)

        # Create state
        memory_unique = {}
        memory_primary = {}
        foreign_groups = []
        is_integrity = bool(schema.primary_key)
        for field in schema.fields:
            if field.constraints.get("unique"):
                memory_unique[field.name] = {}
                is_integrity = True
        if self.__lookup:
            for fk in schema.foreign_keys:
                group = {}
                group["sourceName"] = fk["reference"]["resource"]
                group["sourceKey"] = tuple(fk["reference"]["fields"])
                group["targetKey"] = tuple(fk["fields"])
                foreign_groups.append(group)
                is_integrity = True

        # Stream rows
        for cells in self.__list_stream:

            # Skip header
            if not self.__row_number:
                continue

            # Create row
            row = Row(
                cells,
                field_info=field_info,
                row_position=self.__row_position,
                row_number=self.__row_number,
            )

            # Unique Error
            if is_integrity and memory_unique:
                for field_name in memory_unique.keys():
                    cell = row[field_name]
                    if cell is not None:
                        match = memory_unique[field_name].get(cell)
                        memory_unique[field_name][cell] = row.row_position
                        if match:
                            Error = errors.UniqueError
                            note = "the same as in the row at position %s" % match
                            error = Error.from_row(row, note=note, field_name=field_name)
                            row.errors.append(error)

            # Primary Key Error
            if is_integrity and schema.primary_key:
                cells = tuple(row[field_name] for field_name in schema.primary_key)
                if set(cells) == {None}:
                    note = 'cells composing the primary keys are all "None"'
                    error = errors.PrimaryKeyError.from_row(row, note=note)
                    row.errors.append(error)
                else:
                    match = memory_primary.get(cells)
                    memory_primary[cells] = row.row_position
                    if match:
                        if match:
                            note = "the same as in the row at position %s" % match
                            error = errors.PrimaryKeyError.from_row(row, note=note)
                            row.errors.append(error)

            # Foreign Key Error
            if is_integrity and foreign_groups:
                for group in foreign_groups:
                    group_lookup = self.__lookup.get(group["sourceName"])
                    if group_lookup:
                        cells = tuple(row[name] for name in group["targetKey"])
                        if set(cells) == {None}:
                            continue
                        match = cells in group_lookup.get(group["sourceKey"], set())
                        if not match:
                            note = "not found in the lookup table"
                            error = errors.ForeignKeyError.from_row(row, note=note)
                            row.errors.append(error)

            # Handle errors
            if self.onerror != "ignore":
                if not row.valid:
                    error = row.errors[0]
                    if self.onerror == "raise":
                        raise FrictionlessException(error)
                    warnings.warn(error.message, UserWarning)

            # Stream rows
            yield row

    def __read_header(self):

        # Create header
        header = Header(
            self.__labels,
            fields=self.schema.fields,
            field_positions=self.__field_positions,
            row_positions=self.layout.header_rows,
            ignore_case=not self.layout.header_case,
        )

        # Handle errors
        if not header.valid:
            error = header.errors[0]
            if self.onerror == "warn":
                warnings.warn(error.message, UserWarning)
            elif self.onerror == "raise":
                raise FrictionlessException(error)

        return header

    def __read_list_stream(self):

        # Prepare context
        self.__row_number = 0
        self.__row_position = 0
        parser_iterator = self.__read_iterate_parser()
        fragment_iterator = zip(self.__fragment_positions, self.__fragment)

        # Stream header
        if self.__header is not None:
            yield self.header.to_list()

        # Stream fragment/parser (no filtering)
        if not self.layout:
            for row_position, cells in chain(fragment_iterator, parser_iterator):
                self.__row_position = row_position
                self.__row_number += 1
                self.stats["rows"] = self.__row_number
                yield cells
            return

        # Stream fragment/parser (with filtering)
        limit = self.layout.limit_rows
        offset = self.layout.offset_rows or 0
        for row_position, cells in chain(fragment_iterator, parser_iterator):
            if offset:
                offset -= 1
                continue
            self.__row_position = row_position
            self.__row_number += 1
            self.stats["rows"] = self.__row_number
            yield cells
            if limit and limit <= self.__row_number:
                break

    def __read_iterate_parser(self):

        # Prepare context
        start = max(self.__fragment_positions or [0]) + 1
        iterator = enumerate(self.__parser.list_stream, start=start)

        # Stream without filtering
        if not self.layout:
            yield from iterator
            return

        # Stream with filtering
        for row_position, cells in iterator:
            if self.layout.read_filter_rows(cells, row_position):
                cells = self.layout.read_filter_cells(cells, self.__field_positions)
                yield row_position, cells

    def __read_infer_sample(self):

        # Create state
        sample = []
        fragment = []
        labels = []
        field_positions = []
        fragment_positions = []

        # Prepare header
        widths = []
        for row_position, cells in enumerate(self.__parser.list_stream, start=1):
            sample.append(cells)
            widths.append(len(cells))
            if len(widths) >= self.__detector.sample_size:
                break

        # Infer header
        row_number = 0
        layout = self.layout
        if layout.get("header") is None and layout.get("headerRows") is None and widths:
            layout["header"] = False
            width = round(sum(widths) / len(widths))
            drift = max(round(width * 0.1), 1)
            match = list(range(width - drift, width + drift + 1))
            for row_position, cells in enumerate(sample, start=1):
                if self.layout.read_filter_rows(cells, row_position):
                    row_number += 1
                    if len(cells) not in match:
                        continue
                    if not helpers.is_only_strings(cells):
                        continue
                    del layout["header"]
                    if row_number != config.DEFAULT_HEADER_ROWS[0]:
                        layout["headerRows"] = [row_number]
                    break
            # TODO: remove this hack (stop editing default layout above)
            if not layout:
                self.pop("layout", None)

        # Infer layout
        row_number = 0
        header_data = []
        header_ready = False
        header_row_positions = []
        header_numbers = layout.header_rows or config.DEFAULT_HEADER_ROWS
        for row_position, cells in enumerate(sample, start=1):
            if self.layout.read_filter_rows(cells, row_position):
                row_number += 1

                # Labels
                if not header_ready:
                    if row_number in header_numbers:
                        header_data.append(helpers.stringify_label(cells))
                        if layout.header:
                            header_row_positions.append(row_position)
                    if row_number >= max(header_numbers):
                        labels, field_positions = self.__read_infer_header(header_data)
                        header_ready = True
                    if not header_ready or layout.header:
                        continue

                # Fragment
                fragment.append(self.layout.read_filter_cells(cells, field_positions))
                fragment_positions.append(row_position)

        # Detect schema
        self.schema = self.__detector.detect_schema(
            fragment,
            labels=labels,
            schema=self.schema,
        )

        # Store state
        self.__sample = sample
        self.__fragment = fragment
        self.__labels = labels
        self.__field_positions = field_positions
        self.__fragment_positions = fragment_positions

        # Store stats
        self.stats["fields"] = len(self.schema.fields)

    def __read_infer_header(self, header_data):
        layout = self.layout

        # No header
        if not layout.header:
            return [], list(range(1, len(header_data[0]) + 1))

        # Get labels
        labels = []
        prev_cells = {}
        for cells in header_data:
            for index, cell in enumerate(cells):
                if prev_cells.get(index) == cell:
                    continue
                prev_cells[index] = cell
                if len(labels) <= index:
                    labels.append(cell)
                    continue
                labels[index] = layout.header_join.join([labels[index], cell])

        # Filter labels
        filter_labels = []
        field_positions = []
        limit = self.layout.limit_fields
        offset = self.layout.offset_fields or 0
        for field_position, labels in enumerate(labels, start=1):
            if self.layout.read_filter_fields(labels, field_position):
                if offset:
                    offset -= 1
                    continue
                filter_labels.append(labels)
                field_positions.append(field_position)
                if limit and limit <= len(filter_labels):
                    break

        return filter_labels, field_positions

    def __read_prepare_lookup(self):
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
            if source_name:
                if not self.__package.has_resource(source_name):
                    note = f'Failed to handle a foreign key for resource "{self.name}" as resource "{source_name}" does not exist'
                    raise FrictionlessException(errors.ResourceError(note=note))
                source_res = self.__package.get_resource(source_name)
            else:
                source_res = self.to_copy(nolookup=True)
            lookup.setdefault(source_name, {})
            if source_key in lookup[source_name]:
                continue
            lookup[source_name][source_key] = set()
            if not source_res:
                continue
            with source_res:
                for row in source_res.row_stream:
                    cells = tuple(row.get(field_name) for field_name in source_key)
                    if set(cells) == {None}:
                        continue
                    lookup[source_name][source_key].add(cells)
        return lookup

    def __read_raise_closed(self):
        if not self.__list_stream or not self.__row_stream:
            note = 'the resource has not been opened by "resource.open()"'
            raise FrictionlessException(errors.ResourceError(note=note))

    # Write

    # TODO: allow passing source, **options and return Resource?
    # TODO: what we should return?
    # TODO: use contextlib.closing?
    # TODO: should we set target.data?
    def write(self, target):
        """Write this resource to the target resource

        Parameters:
            target (Resource): target Resource
        """
        parser = system.create_parser(target)
        read_row_stream = self.__write_row_stream_create
        result = parser.write_row_stream(read_row_stream)
        return result

    def __write_row_stream_create(self):
        if self.closed or self.__row_position:
            self.open()
        return self.row_stream

    # Import/Export

    @staticmethod
    def from_petl(storage, *, view, **options):
        """Create a resource from PETL container"""
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
    def from_ckan(*, name, url, dataset, apikey=None):
        """Import resource from CKAN

        Parameters:
            name (string): resource name
            url (string): CKAN instance url e.g. "https://demo.ckan.org"
            dataset (string): dataset id in CKAN e.g. "my-dataset"
            apikey? (str): API key for CKAN e.g. "51912f57-a657-4caa-b2a7-0a1c16821f4b"
        """
        return Resource.from_storage(
            system.create_storage(
                "ckan",
                url=url,
                dataset=dataset,
                apikey=apikey,
            ),
            name=name,
        )

    @staticmethod
    def from_sql(*, name, url=None, engine=None, prefix="", namespace=None):
        """Import resource from SQL table

        Parameters:
            name (str): resource name
            url? (string): SQL connection string
            engine? (object): `sqlalchemy` engine
            prefix? (str): prefix for all tables
            namespace? (str): SQL scheme
        """
        return Resource.from_storage(
            system.create_storage(
                "sql", url=url, engine=engine, prefix=prefix, namespace=namespace
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

    def to_copy(self, **options):
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
            **options,
        )

    def to_petl(self, *, normalize=False):
        resource = self

        # Define view
        class ResourceView(petl.Table):
            def __iter__(self):
                with helpers.ensure_open(resource):
                    if normalize:
                        yield resource.schema.field_names
                        yield from (row.to_list() for row in resource.row_stream)
                        return
                    if not resource.layout.header:
                        yield resource.schema.field_names
                    yield from resource.list_stream

        return ResourceView()

    def to_storage(self, storage, *, force=False):
        """Export resource to storage

        Parameters:
            storage (Storage): storage instance
            force (bool): overwrite existent
        """
        storage.write_resource(self.to_copy(), force=force)
        return storage

    def to_ckan(self, *, url, dataset, apikey=None, force=False):
        """Export resource to CKAN

        Parameters:
            url (string): CKAN instance url e.g. "https://demo.ckan.org"
            dataset (string): dataset id in CKAN e.g. "my-dataset"
            apikey? (str): API key for CKAN e.g. "51912f57-a657-4caa-b2a7-0a1c16821f4b"
            force (bool): (optional) overwrite existing data
        """
        return self.to_storage(
            system.create_storage(
                "ckan",
                url=url,
                dataset=dataset,
                apikey=apikey,
            ),
            force=force,
        )

    def to_sql(self, *, url=None, engine=None, prefix="", namespace=None, force=False):
        """Export resource to SQL table

        Parameters:
            url? (string): SQL connection string
            engine? (object): `sqlalchemy` engine
            prefix? (str): prefix for all tables
            namespace? (str): SQL scheme
            force? (bool): overwrite existent
        """
        return self.to_storage(
            system.create_storage(
                "sql", url=url, engine=engine, prefix=prefix, namespace=namespace
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
    metadata_profile["properties"]["control"] = {"type": ["string", "object"]}
    metadata_profile["properties"]["dialect"] = {"type": ["string", "object"]}
    metadata_profile["properties"]["layout"] = {"type": ["string", "object"]}
    metadata_profile["properties"]["schema"] = {"type": ["string", "object"]}

    def metadata_process(self):

        # File
        self.__file = system.create_file(
            self.get("data", self.get("path", [])),
            innerpath=self.get("innerpath"),
            basepath=self.__basepath,
        )

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

        # Layout
        layout = self.get("layout")
        if not isinstance(layout, (str, type(None), Layout)):
            layout = Layout(layout)
            dict.__setitem__(self, "layout", layout)

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
                    raise FrictionlessException(error)

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Control
        if self.control:
            yield from self.control.metadata_errors

        # Dialect
        if self.dialect:
            yield from self.dialect.metadata_errors

        # Layout
        if self.layout:
            yield from self.layout.metadata_errors

        # Schema
        if self.schema:
            yield from self.schema.metadata_errors
