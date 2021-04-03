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


# NOTE:
# Consider making resource.stats unavailable until it's fully calculated
# Also, review the situation with describe function removing stats (move to infer?)


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
        self.__labels = None
        self.__fragment = None
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
        self.__package = package

        # Store specs
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
        with helpers.ensure_open(self):
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
        if self.tabular:
            default = config.DEFAULT_TABULAR_RESOURCE_PROFILE
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
            dialect = helpers.join_path(self.basepath, dialect)
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
            schema = Schema(helpers.join_path(self.basepath, schema))
            schema = self.metadata_attach("schema", schema)
        return schema

    @Metadata.property
    def stats(self):
        """
        Returns
            dict?: resource stats
        """
        stats = self.get("stats")
        if stats is None:
            stats = {"hash": "", "bytes": 0}
            if self.tabular:
                stats.update({"fields": 0, "rows": 0})
            stats = self.metadata_attach("stats", stats)
        return stats

    @property
    def buffer(self):
        """File's bytes used as a sample

        These buffer bytes are used to infer characteristics of the
        source file (e.g. encoding, ...).

        Returns:
            bytes?: file buffer
        """
        if self.__parser and self.__parser.loader:
            return self.__parser.loader.buffer
        if self.__loader:
            return self.__loader.buffer

    @property
    def sample(self):
        """Table's lists used as sample.

        These sample rows are used to infer characteristics of the
        source file (e.g. schema, ...).

        Returns:
            list[]?: table sample
        """
        return self.__sample

    @property
    def labels(self):
        """
        Returns:
            str[]?: table labels
        """
        return self.__labels

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
    def header(self):
        """
        Returns:
            str[]?: table header
        """
        return self.__header

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
        return self.__file.memory

    @Metadata.property(write=False)
    def remote(self):
        return self.__file.remote

    @Metadata.property(write=False)
    def multipart(self):
        return self.__file.multipart

    @Metadata.property(write=False)
    def tabular(self):
        """
        Returns
            bool: if resource is tabular
        """
        if not self.closed:
            return bool(self.__parser)
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
        if not self.closed:
            if not self.__loader:
                self.__loader = system.create_loader(self)
                self.__loader.open()
            return self.__loader.byte_stream

    @property
    def text_stream(self):
        """Text stream in form of a generator

        Yields:
            gen<str[]>?: text stream
        """
        if not self.closed:
            if not self.__loader:
                self.__loader = system.create_loader(self)
                self.__loader.open()
            return self.__loader.text_stream

    @property
    def list_stream(self):
        """List stream in form of a generator

        Yields:
            gen<any[][]>?: list stream
        """
        if self.__parser:
            return self.__parser.list_stream

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
        if not self.closed:
            note = "Resource.infer canot be used on a open resource"
            raise FrictionlessException(errors.ResourceError(note=note))
        with self:
            if not stats:
                self.pop("stats", None)
                return
            stream = self.row_stream or self.byte_stream
            helpers.pass_through(stream)

    # Open/Close

    def open(self):
        """Open the resource as "io.open" does

        Raises:
            FrictionlessException: any exception that occurs
        """
        self.close()

        # Infer
        self.pop("stats", None)
        self["name"] = self.name
        self["profile"] = self.profile
        self["scheme"] = self.scheme
        self["format"] = self.format
        self["hashing"] = self.hashing
        if self.innerpath:
            self["innerpath"] = self.innerpath
        if self.compression:
            self["compression"] = self.compression
        if self.control:
            self["control"] = self.control
        if self.dialect:
            self["dialect"] = self.dialect
        self["stats"] = self.stats

        # Validate
        if self.metadata_errors:
            error = self.metadata_errors[0]
            raise FrictionlessException(error)

        # Open
        try:

            # Table
            if self.tabular:
                self.__parser = system.create_parser(self)
                self.__parser.open()
                self.__read_detect_layout()
                self.__read_detect_schema()
                self.__read_detect_lookup()
                self.__header = self.__read_header()
                self.__row_stream = self.__read_row_stream()
                return self

            # File
            else:
                self.__loader = system.create_loader(self)
                self.__loader.open()
                return self

        # Error
        except Exception:
            self.close()
            raise

    def close(self):
        """Close the table as "filelike.close" does"""
        if self.__parser:
            self.__parser.close()
            self.__parser = None
        if self.__loader:
            self.__loader.close()
            self.__loader = None

    @property
    def closed(self):
        """Whether the table is closed

        Returns:
            bool: if closed
        """
        return self.__parser is None and self.__loader is None

    # Read

    def read_bytes(self, *, size=None):
        """Read bytes into memory

        Returns:
            any[][]: resource bytes
        """
        if self.memory:
            return b""
        with helpers.ensure_open(self):
            return self.byte_stream.read1(size)

    def read_text(self, *, size=None):
        """Read text into memory

        Returns:
            str: resource text
        """
        if self.memory:
            return ""
        with helpers.ensure_open(self):
            return self.text_stream.read(size)

    def read_data(self, *, size=None):
        """Read data into memory

        Returns:
            any: resource data
        """
        if self.data:
            return self.data
        with helpers.ensure_open(self):
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
            for cells in self.list_stream:
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
            for row in self.row_stream:
                rows.append(row)
                if size and len(rows) >= size:
                    break
            return rows

    def __read_row_stream(self):

        # During row streaming we crate a field inf structure
        # This structure is optimized and detached version of schema.fields
        # We create all data structures in-advance to share them between rows

        # Create field info
        field_number = 0
        field_info = {"names": [], "objects": [], "positions": [], "mapping": {}}
        iterator = zip_longest(self.schema.fields, self.__field_positions)
        for field, field_position in iterator:
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
        is_integrity = bool(self.schema.primary_key)
        for field in self.schema.fields:
            if field.constraints.get("unique"):
                memory_unique[field.name] = {}
                is_integrity = True
        if self.__lookup:
            for fk in self.schema.foreign_keys:
                group = {}
                group["sourceName"] = fk["reference"]["resource"]
                group["sourceKey"] = tuple(fk["reference"]["fields"])
                group["targetKey"] = tuple(fk["fields"])
                foreign_groups.append(group)
                is_integrity = True

        # Create iterator
        iterator = chain(
            zip(self.__fragment_positions, self.__fragment),
            self.__read_list_stream(),
        )

        # Create row stream
        def row_stream():
            self.__row_number = 0
            limit = self.layout.limit_rows
            offset = self.layout.offset_rows or 0
            for row_position, cells in iterator:
                self.__row_position = row_position

                # Offset/offset rows
                if offset:
                    offset -= 1
                    continue
                if limit and limit <= self.__row_number:
                    break

                # Create row
                self.__row_number += 1
                self.stats["rows"] = self.__row_number
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
                                func = errors.UniqueError.from_row
                                note = "the same as in the row at position %s" % match
                                error = func(row, note=note, field_name=field_name)
                                row.errors.append(error)

                # Primary Key Error
                if is_integrity and self.schema.primary_key:
                    cells = tuple(row[name] for name in self.schema.primary_key)
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

                # Yield row
                yield row

        # Return row stream
        return row_stream()

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

        # Prepare iterator
        iterator = (
            (position, cells)
            for position, cells in enumerate(self.__parser.list_stream, start=1)
            if position > len(self.__parser.sample)
        )

        # Stream without filtering
        if not self.layout:
            yield from iterator
            return

        # Stream with filtering
        for row_position, cells in iterator:
            if self.layout.read_filter_rows(cells, row_position=row_position):
                yield row_position, self.layout.read_filter_cells(
                    cells, field_positions=self.__field_positions
                )

    def __read_detect_layout(self):
        sample = self.__parser.sample
        layout = self.detector.detect_layout(sample, layout=self.layout)
        if layout:
            self.layout = layout
        self.__sample = sample

    def __read_detect_schema(self):
        labels, field_positions = self.layout.read_labels(self.sample)
        fragment, fragment_positions = self.layout.read_fragment(self.sample)
        schema = self.detector.detect_schema(fragment, labels=labels, schema=self.schema)
        if schema:
            self.schema = schema
        self.__labels = labels
        self.__fragment = fragment
        self.__field_positions = field_positions
        self.__fragment_positions = fragment_positions
        self.stats["fields"] = len(schema.fields)
        # NOTE: review whether it's a proper place for this fallback to data resource
        if not schema:
            self.profile = "data-resource"

    def __read_detect_lookup(self):
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
                source_res = self.to_copy()
            source_res.schema.pop("foreignKeys", None)
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
        self.__lookup = lookup

    # Write

    def write(self, target=None, **options):
        """Write this resource to the target resource

        Parameters:
            target (any|Resource): target or target resource instance
            **options (dict): Resource constructor options
        """
        native = isinstance(target, Resource)
        target = target.to_copy() if native else Resource(target, **options)
        parser = system.create_parser(target)
        parser.write_row_stream(self.to_copy())
        return target

    # Import/Export

    def to_dict(self):
        """Create a dict from the resource

        Returns
            dict: dict representation
        """
        # Data can be not serializable (generators/functions)
        descriptor = super().to_dict()
        data = descriptor.pop("data", None)
        if isinstance(data, list):
            descriptor["data"] = data
        return descriptor

    def to_copy(self, **options):
        """Create a copy from the resource

        Returns
            Resource: resource copy
        """
        descriptor = self.to_dict()
        return Resource(
            descriptor,
            data=self.data,
            basepath=self.__basepath,
            onerror=self.__onerror,
            trusted=self.__trusted,
            package=self.__package,
            **options,
        )

    def to_view(self, type="look", **options):
        """Create a view from the resource

        See PETL's docs for more information:
        https://petl.readthedocs.io/en/stable/util.html#visualising-tables

        Parameters:
            type (look|lookall|see|display|displayall): view's type
            **options (dict): options to be passed to PETL

        Returns
            str: resource's view
        """
        assert type in ["look", "lookall", "see", "display", "displayall"]
        view = str(getattr(self.to_petl(normalize=True), type)(**options))
        return view

    def to_snap(self):
        """Create a snapshot from the resource

        Returns
            list: resource's data
        """
        snap = []
        with helpers.ensure_open(self):
            snap.append(self.header.to_list())
            for row in self.row_stream:
                snap.append(row.to_list())
        return snap

    def to_inline(self, *, dialect=None):
        """Helper to export resource as an inline data"""
        target = self.write(Resource(format="inline", dialect=dialect))
        return target.data

    def to_pandas(self, *, dialect=None):
        """Helper to export resource as an Pandas dataframe"""
        target = self.write(Resource(format="pandas", dialect=dialect))
        return target.data

    @staticmethod
    def from_petl(view, **options):
        """Create a resource from PETL view"""
        return Resource(data=view, **options)

    def to_petl(self, normalize=False):
        """Export resource as a PETL table"""
        resource = self.to_copy()

        # Define view
        class ResourceView(petl.Table):
            def __iter__(self):
                with resource:
                    if normalize:
                        yield resource.schema.field_names
                        yield from (row.to_list() for row in resource.row_stream)
                        return
                    if not resource.header.missing:
                        yield resource.header.labels
                    yield from (row.cells for row in resource.row_stream)

        return ResourceView()

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

        # Control/Dialect
        yield from self.control.metadata_errors
        yield from self.dialect.metadata_errors

        # Layout/Schema
        if self.layout:
            yield from self.layout.metadata_errors
        if self.schema:
            yield from self.schema.metadata_errors
