import os
import petl
import typing
import warnings
from pathlib import Path
from copy import deepcopy
from itertools import zip_longest, chain
from .exception import FrictionlessException
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


# TODO: make automatically trusted if path is passed not from descriptor
# TODO: merge docstrings from Table
# TODO: Add mediatype from the specs?
# TODO: Remove support for deprecated "url"?
# TODO: Support hash/bytes/rows from the specs?
class Resource(Metadata):
    """Resource representation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Resource`

    Parameters:
        descriptor? (str|dict): resource descriptor
        name? (str): resource name (for machines)
        title? (str): resource title (for humans)
        descriptor? (str): resource descriptor
        licenses? (dict[]): resource licenses
        sources? (dict[]): resource sources
        path? (str): file path
        data? (any[][]): array or data arrays
        scheme? (str): file scheme
        format? (str): file format
        hashing? (str): file hashing
        encoding? (str): file encoding
        innerpath? (str): file compression path
        compression? (str): file compression
        control? (dict): file control
        dialect? (dict): table dialect
        layout? (dict): table layout
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
        source=None,
        *,
        descriptor=None,
        # Spec
        name=None,
        title=None,
        description=None,
        licenses=None,
        sources=None,
        profile=None,
        path=None,
        data=None,
        # File
        scheme=None,
        format=None,
        hashing=None,
        encoding=None,
        innerpath=None,
        compression=None,
        # Control/Dialect
        control=None,
        dialect=None,
        # Layout/Schema
        layout=None,
        schema=None,
        sync_schema=False,
        patch_schema=None,
        # Infer
        infer_type=None,
        infer_names=None,
        infer_volume=config.DEFAULT_INFER_VOLUME,
        infer_confidence=config.DEFAULT_INFER_CONFIDENCE,
        infer_float_numbers=config.DEFAULT_FLOAT_NUMBER,
        infer_missing_values=config.DEFAULT_MISSING_VALUES,
        # Misc
        stats=None,
        basepath="",
        onerror="ignore",
        trusted=False,
        package=None,
        nolookup=False,
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

        # Store state
        self.__loader = None
        self.__parser = None
        self.__sample = None
        self.__header = None
        self.__lookup = None
        self.__byte_stream = None
        self.__text_stream = None
        self.__data_stream = None
        self.__row_stream = None
        self.__row_number = None
        self.__row_position = None
        self.__field_positions = None
        self.__sample_positions = None

        # Store params
        self.__sync_schema = sync_schema
        self.__patch_schema = patch_schema
        self.__infer_type = infer_type
        self.__infer_names = infer_names
        self.__infer_volume = infer_volume
        self.__infer_confidence = infer_confidence
        self.__infer_float_numbers = infer_float_numbers
        self.__infer_missing_values = infer_missing_values
        self.__basepath = basepath or helpers.detect_basepath(descriptor)
        self.__onerror = onerror
        self.__trusted = trusted
        self.__package = package
        self.__nolookup = nolookup

        # Set properties
        self.setinitial("name", name)
        self.setinitial("title", title)
        self.setinitial("description", description)
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

    @property
    def sample(self):
        """Tables's rows used as sample.

        These sample rows are used internally to infer characteristics of the
        source file (e.g. schema, ...).

        Returns:
            list[]?: table sample
        """
        return self.__sample

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
            gen<str[]>?: data stream
        """
        return self.__text_stream

    @property
    def data_stream(self):
        """Data stream in form of a generator

        Yields:
            gen<any[][]>?: data stream
        """
        return self.__data_stream

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
            self["innerpath"] = self.innerpath
            self["compression"] = self.compression
            if self.tabular:
                self["dialect"] = self.dialect
                self["layout"] = self.layout
                # TODO: where is control/schema?
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
            if not self.__nolookup:
                self.__lookup = self.__read_prepare_lookup()
            if self.__parser.loader:
                self.__byte_stream = self.__parser.loader.byte_stream
            if self.__parser.loader:
                self.__text_stream = self.__parser.loader.text_stream
            self.__data_stream = self.__read_data_stream()
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

    def read_bytes(self):
        """Read data into memory

        Returns:
            any[][]: table data
        """
        # TODO: rework when there is proper sample caching
        if self.memory:
            return b""
        self["stats"] = {"hash": "", "bytes": 0, "fields": 0, "rows": 0}
        with system.create_loader(self) as loader:
            return loader.byte_stream.read1()

    def read_text(self):
        """Read text into memory

        Returns:
            str: table data
        """
        # TODO: rework when there is proper sample caching
        if self.memory:
            return ""
        self["stats"] = {"hash": "", "bytes": 0, "fields": 0, "rows": 0}
        with system.create_loader(self) as loader:
            result = ""
            for line in loader.text_stream:
                result += line
            return result

    def read_data(self):
        """Read data into memory

        Returns:
            any[][]: table data
        """
        with helpers.ensure_open(self):
            if self.__data_stream:
                return list(self.__data_stream)
            return []

    def read_rows(self):
        """Read rows into memory

        Returns:
            Row[]: table rows
        """
        with helpers.ensure_open(self):
            if self.__row_stream:
                return list(self.__row_stream)
            return []

    def __read_row_stream(self):
        schema = self.schema

        # Handle header errors
        if self.header is not None:
            if not self.header.valid:
                error = self.header.errors[0]
                if self.onerror == "warn":
                    warnings.warn(error.message, UserWarning)
                elif self.onerror == "raise":
                    raise FrictionlessException(error)

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
        for cells in self.__data_stream:

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

            # Handle row errors
            if self.onerror != "ignore":
                if not row.valid:
                    error = row.errors[0]
                    if self.onerror == "raise":
                        raise FrictionlessException(error)
                    warnings.warn(error.message, UserWarning)

            # Stream rows
            yield row

    def __read_data_stream(self):

        # Prepare context
        self.__row_number = 0
        self.__row_position = 0
        parser_iterator = self.__read_iterate_parser()
        sample_iterator = zip(self.__sample_positions, self.__sample)

        # Stream header
        if self.__header is not None:
            yield self.header.to_list()

        # Stream sample/parser (no filtering)
        if not self.layout:
            for row_position, cells in chain(sample_iterator, parser_iterator):
                self.__row_position = row_position
                self.__row_number += 1
                self.stats["rows"] = self.__row_number
                yield cells
            return

        # Stream sample/parser (with filtering)
        limit = self.layout.limit_rows
        offset = self.layout.offset_rows or 0
        for row_position, cells in chain(sample_iterator, parser_iterator):
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
        start = max(self.__sample_positions or [0]) + 1
        iterator = enumerate(self.__parser.data_stream, start=start)

        # Stream without filtering
        if not self.layout:
            yield from iterator
            return

        # Stream with filtering
        for row_position, cells in iterator:
            if self.__read_filter_rows(row_position, cells):
                cells = self.__read_filter_cells(cells, self.__field_positions)
                yield row_position, cells

    def __read_infer_sample(self):

        # Create state
        sample = []
        labels = []
        field_positions = []
        sample_positions = []

        # Prepare header
        buffer = []
        widths = []
        for row_position, cells in enumerate(self.__parser.data_stream, start=1):
            buffer.append(cells)
            if self.__read_filter_rows(row_position, cells):
                widths.append(len(cells))
                if len(widths) >= self.__infer_volume:
                    break

        # Infer header
        row_number = 0
        layout = self.layout
        if layout.get("header") is None and layout.get("headerRows") is None and widths:
            layout["header"] = False
            width = round(sum(widths) / len(widths))
            drift = max(round(width * 0.1), 1)
            match = list(range(width - drift, width + drift + 1))
            for row_position, cells in enumerate(buffer, start=1):
                if self.__read_filter_rows(row_position, cells):
                    row_number += 1
                    if len(cells) not in match:
                        continue
                    if not helpers.is_only_strings(cells):
                        continue
                    del layout["header"]
                    if row_number != config.DEFAULT_HEADER_ROWS[0]:
                        layout["headerRows"] = [row_number]
                    break

        # Infer table
        row_number = 0
        header_data = []
        header_ready = False
        header_row_positions = []
        header_numbers = layout.header_rows or config.DEFAULT_HEADER_ROWS
        iterator = chain(buffer, self.__parser.data_stream)
        for row_position, cells in enumerate(iterator, start=1):
            if self.__read_filter_rows(row_position, cells):
                row_number += 1

                # Header
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

                # Sample
                sample.append(self.__read_filter_cells(cells, field_positions))
                sample_positions.append(row_position)
                if len(sample) >= self.__infer_volume:
                    break

        # Infer schema
        if not self.schema.fields:
            self.schema = Schema.from_sample(
                sample,
                type=self.__infer_type,
                names=self.__infer_names or labels,
                confidence=self.__infer_confidence,
                float_numbers=self.__infer_float_numbers,
                missing_values=self.__infer_missing_values,
            )

        # Sync schema
        if self.__sync_schema:
            fields = []
            mapping = {field.get("name"): field for field in self.schema.fields}
            for name in labels:
                fields.append(mapping.get(name, {"name": name, "type": "any"}))
            self.schema.fields = fields

        # Patch schema
        if self.__patch_schema:
            patch_schema = deepcopy(self.__patch_schema)
            fields = patch_schema.pop("fields", {})
            self.schema.update(patch_schema)
            for field in self.schema.fields:
                field.update((fields.get(field.get("name"), {})))

        # Validate schema
        # TODO: reconsider this - not perfect for transform
        if len(self.schema.field_names) != len(set(self.schema.field_names)):
            note = "Schemas with duplicate field names are not supported"
            raise FrictionlessException(errors.SchemaError(note=note))

        # Store stats
        self.stats["fields"] = len(self.schema.fields)

        # Store state
        self.__sample = sample
        self.__field_positions = field_positions
        self.__sample_positions = sample_positions
        self.__header = Header(
            labels,
            fields=self.schema.fields,
            field_positions=field_positions,
            row_positions=header_row_positions,
            ignore_case=not layout.header_case,
        )

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
            if self.__read_filter_fields(field_position, labels):
                if offset:
                    offset -= 1
                    continue
                filter_labels.append(labels)
                field_positions.append(field_position)
                if limit and limit <= len(filter_labels):
                    break

        return filter_labels, field_positions

    def __read_filter_fields(self, field_position, header):
        match = True
        for name in ["pick", "skip"]:
            if name == "pick":
                items = self.layout.pick_fields_compiled
            else:
                items = self.layout.skip_fields_compiled
            if not items:
                continue
            match = match and name == "skip"
            for item in items:
                if item == "<blank>" and header == "":
                    match = not match
                elif isinstance(item, str) and item == header:
                    match = not match
                elif isinstance(item, int) and item == field_position:
                    match = not match
                elif isinstance(item, typing.Pattern) and item.match(header):
                    match = not match
        return match

    def __read_filter_rows(self, row_position, cells):
        match = True
        cell = cells[0] if cells else None
        cell = "" if cell is None else str(cell)
        for name in ["pick", "skip"]:
            if name == "pick":
                items = self.layout.pick_rows_compiled
            else:
                items = self.layout.skip_rows_compiled
            if not items:
                continue
            match = match and name == "skip"
            for item in items:
                if item == "<blank>":
                    if not any(cell for cell in cells if cell not in ["", None]):
                        match = not match
                elif isinstance(item, str):
                    if item == cell or (item and cell.startswith(item)):
                        match = not match
                elif isinstance(item, int) and item == row_position:
                    match = not match
                elif isinstance(item, typing.Pattern) and item.match(cell):
                    match = not match
        return match

    def __read_filter_cells(self, cells, field_positions):
        if self.layout.is_field_filtering:
            result = []
            for field_position, cell in enumerate(cells, start=1):
                if field_position in field_positions:
                    result.append(cell)
            return result
        return cells

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
        if not self.__data_stream or not self.__row_stream:
            note = 'the resource has not been opened by "resource.open()"'
            raise FrictionlessException(errors.Error(note=note))

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
                    yield from resource.data_stream

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
