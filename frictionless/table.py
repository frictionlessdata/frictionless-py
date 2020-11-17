import typing
import warnings
from pathlib import Path
from copy import deepcopy
from itertools import chain
from .resource import Resource
from .system import system
from .header import Header
from .row import Row
from . import exceptions
from . import errors
from . import helpers
from . import config


class Table:
    """Table representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Table`

    This class is at heart of the whole Frictionless framwork.
    It loads a data source, and allows you to stream its parsed contents.

    ```python
    with Table("data/table.csv") as table:
        table.header == ["id", "name"]
        table.read_rows() == [
            {'id': 1, 'name': 'english'},
            {'id': 2, 'name': '中国人'},
        ]
    ```

    Parameters:

        source (any): Source of the file; can be in various forms.
            Usually, it's a string as `<scheme>://path/to/file.<format>`.
            It also can be, for example, an array of data arrays/dictionaries.

        scheme? (str): Scheme for loading the file (file, http, ...).
            If not set, it'll be inferred from `source`.

        format? (str): File source's format (csv, xls, ...).
            If not set, it'll be inferred from `source`.

        hashing? (str): An algorithm to hash data.
            It defaults to 'md5'.

        encoding? (str): Source encoding.
            If not set, it'll be inferred from `source`.

        compression? (str): Source file compression (zip, ...).
            If not set, it'll be inferred from `source`.

        compression_path? (str): A path within the compressed file.
            It defaults to the first file in the archive.

        control? (dict|Control): File control.
            For more infromation, please check the Control documentation.

        dialect? (dict|Dialect): Table dialect.
            For more infromation, please check the Dialect documentation.

        query? (dict|Query): Table query.
            For more infromation, please check the Query documentation.

        headers? (int|int[]|[int[], str]): Either a row
            number or list of row numbers (in case of multi-line headers) to be
            considered as headers (rows start counting at 1), or a pair
            where the first element is header rows and the second the
            header joiner.  It defaults to 1.

        schema? (dict|Schema): Table schema.
            For more infromation, please check the Schema documentation.

        sync_schema? (bool): Whether to sync the schema.
            If it sets to `True` the provided schema will be mapped to
            the inferred schema. It means that, for example, you can
            provide a subset of fileds to be applied on top of the inferred
            fields or the provided schema can have different order of fields.

        patch_schema? (dict): A dictionary to be used as an inferred schema patch.
            The form of this dictionary should follow the Schema descriptor form
            except for the `fields` property which should be a mapping with the
            key named after a field name and the values being a field patch.
            For more information, please check "Extracting Data" guide.

        infer_type? (str): Enforce all the inferred types to be this type.
            For more information, please check "Describing  Data" guide.

        infer_names? (str[]): Enforce all the inferred fields to have provided names.
            For more information, please check "Describing  Data" guide.

        infer_volume? (int): The amount of rows to be extracted as a samle.
            For more information, please check "Describing  Data" guide.
            It defaults to 100

        infer_confidence? (float): A number from 0 to 1 setting the infer confidence.
            If  1 the data is guaranteed to be valid against the inferred schema.
            For more information, please check "Describing  Data" guide.
            It defaults to 0.9

        infer_missing_values? (str[]): String to be considered as missing values.
            For more information, please check "Describing  Data" guide.
            It defaults to `['']`

        onerror? (ignore|warn|raise): Define behaviour if there is an error in the
            header or rows during the reading rows process.
            It defaults to `ignore`.

        lookup? (dict): The lookup is a special object providing relational information.
            For more information, please check "Extracting  Data" guide.
    """

    # Public

    def __init__(
        self,
        source,
        *,
        # File
        scheme=None,
        format=None,
        hashing=None,
        encoding=None,
        compression=None,
        compression_path=None,
        # Control/Dialect/Query/Header
        control=None,
        dialect=None,
        query=None,
        # TODO: rename to header preserving deprecated headers OR just deprecate?
        headers=None,
        # Schema
        schema=None,
        sync_schema=False,
        patch_schema=False,
        # Infer
        infer_type=None,
        infer_names=None,
        infer_volume=config.DEFAULT_INFER_VOLUME,
        infer_confidence=config.DEFAULT_INFER_CONFIDENCE,
        infer_missing_values=config.DEFAULT_MISSING_VALUES,
        # Integrity
        onerror="ignore",
        lookup=None,
    ):

        # Update source
        if isinstance(source, Path):
            source = str(source)

        # Update dialect
        if headers is not None:
            dialect = (dialect or {}).copy()
            if not headers:
                dialect["header"] = False
            elif isinstance(headers, int):
                dialect["headerRows"] = [headers]
            elif isinstance(headers, list):
                dialect["headerRows"] = headers
                if isinstance(headers[0], list):
                    dialect["headerRows"] = headers[0]
                    dialect["headerJoin"] = headers[1]

        # Store state
        self.__parser = None
        self.__sample = None
        self.__header = None
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
        self.__infer_missing_values = infer_missing_values
        self.__lookup = lookup

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
            dialect=dialect,
            query=query,
            schema=schema,
            onerror=onerror,
            trusted=True,
        )

    def __enter__(self):
        if self.closed:
            self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    # TODO: make compatible with petl?
    # TODO: implement the same for resource?
    def __iter__(self):
        self.__read_row_stream_raise_closed()
        yield from self.__row_stream

    @property
    def source(self):
        """
        Returns:
            any: file source
        """
        return self.__resource.source

    @property
    def path(self):
        """
        Returns:
            str: file path
        """
        return self.__resource.path

    @property
    def data(self):
        """
        Returns:
            str: file data
        """
        return self.__resource.data

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
    def query(self):
        """
        Returns:
            Query?: table query
        """
        return self.__resource.query

    @property
    def dialect(self):
        """
        Returns:
            Dialect?: table dialect
        """
        return self.__resource.dialect

    @property
    def schema(self):
        """
        Returns:
            Schema?: table schema
        """
        return self.__resource.schema

    @property
    def stats(self):
        """Table stats

        The stats object has:
            - hash: str - hashing sum
            - bytes: int - number of bytes
            - fields: int - number of fields
            - rows: int - number of rows

        Returns:
            dict?: table stats

        """
        return self.__resource.stats

    @property
    def header(self):
        """
        Returns:
            str[]?: table header
        """
        return self.__header

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
    def data_stream(self):
        """Data stream in form of a generator of data arrays

        Yields:
            any[][]?: data stream
        """
        return self.__data_stream

    @property
    def row_stream(self):
        """Row stream in form of a generator of Row objects

        Yields:
            Row[][]?: row stream
        """
        return self.__row_stream

    # Open/Close

    def open(self):
        """Open the table as "io.open" does

        Raises:
            FrictionlessException: any exception that occurs
        """
        self.close()
        if self.__resource.query.metadata_errors:
            error = self.__resource.query.metadata_errors[0]
            raise exceptions.FrictionlessException(error)
        try:
            self.__resource.stats = {"hash": "", "bytes": 0, "fields": 0, "rows": 0}
            self.__parser = system.create_parser(self.__resource)
            self.__parser.open()
            self.__data_stream = self.__read_data_stream()
            self.__row_stream = self.__read_row_stream()
            self.__row_number = 0
            self.__row_position = 0
            return self
        except exceptions.FrictionlessException as exception:
            self.close()
            # Ensure not found file is a scheme error
            if exception.error.code == "format-error":
                loader = system.create_loader(self.__resource)
                loader.open()
                loader.close()
            raise
        except Exception:
            self.close()
            raise

    def close(self):
        """Close the table as "filelike.close" does"""
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

    def read_data(self):
        """Read data stream into memory

        Returns:
            any[][]: table data
        """
        self.__read_data_stream_raise_closed()
        return list(self.__data_stream)

    def __read_data_stream(self):
        self.__read_data_stream_infer()
        return self.__read_data_stream_create()

    def __read_data_stream_create(self):
        limit = self.__resource.query.limit_rows
        offset = self.__resource.query.offset_rows or 0
        sample_iterator = self.__read_data_stream_create_sample_iterator()
        parser_iterator = self.__read_data_stream_create_parser_iterator()
        for row_position, cells in chain(sample_iterator, parser_iterator):
            self.__row_position = row_position
            if offset:
                offset -= 1
                continue
            self.__row_number += 1
            self.__resource.stats["rows"] = self.__row_number
            yield cells
            if limit and limit <= self.__resource.stats["rows"]:
                break

    def __read_data_stream_create_sample_iterator(self):
        return zip(self.__sample_positions, self.__sample)

    def __read_data_stream_create_parser_iterator(self):
        start = max(self.__sample_positions or [0]) + 1
        iterator = enumerate(self.__parser.data_stream, start=start)
        for row_position, cells in iterator:
            if self.__read_data_stream_pick_skip_row(row_position, cells):
                cells = self.__read_data_stream_filter_data(cells, self.__field_positions)
                yield row_position, cells

    def __read_data_stream_infer(self):

        # Create state
        sample = []
        header = []
        field_positions = []
        sample_positions = []

        # Prepare header
        buffer = []
        widths = []
        for row_position, cells in enumerate(self.__parser.data_stream, start=1):
            buffer.append(cells)
            if self.__read_data_stream_pick_skip_row(row_position, cells):
                widths.append(len(cells))
                if len(widths) >= self.__infer_volume:
                    break

        # Infer header
        row_number = 0
        dialect = self.__resource.dialect
        if dialect.get("header") is None and dialect.get("headerRows") is None and widths:
            dialect["header"] = False
            width = round(sum(widths) / len(widths))
            drift = max(round(width * 0.1), 1)
            match = list(range(width - drift, width + drift + 1))
            for row_position, cells in enumerate(buffer, start=1):
                if self.__read_data_stream_pick_skip_row(row_position, cells):
                    row_number += 1
                    if len(cells) not in match:
                        continue
                    if not helpers.is_only_strings(cells):
                        continue
                    del dialect["header"]
                    if row_number != config.DEFAULT_HEADER_ROWS[0]:
                        dialect["headerRows"] = [row_number]
                    break

        # Infer table
        row_number = 0
        header_data = []
        header_ready = False
        header_numbers = dialect.header_rows or config.DEFAULT_HEADER_ROWS
        iterator = chain(buffer, self.__parser.data_stream)
        for row_position, cells in enumerate(iterator, start=1):
            if self.__read_data_stream_pick_skip_row(row_position, cells):
                row_number += 1

                # Header
                if not header_ready:
                    if row_number in header_numbers:
                        header_data.append(helpers.stringify_header(cells))
                    if row_number >= max(header_numbers):
                        infer = self.__read_data_stream_infer_header
                        header, field_positions = infer(header_data)
                        header_ready = True
                    if not header_ready or dialect.header:
                        continue

                # Sample
                sample.append(self.__read_data_stream_filter_data(cells, field_positions))
                sample_positions.append(row_position)
                if len(sample) >= self.__infer_volume:
                    break

        # Infer schema
        schema = self.__resource.schema
        if not schema.fields:
            schema.infer(
                sample,
                type=self.__infer_type,
                names=self.__infer_names or header,
                confidence=self.__infer_confidence,
                missing_values=self.__infer_missing_values,
            )

        # Sync schema
        if self.__sync_schema:
            fields = []
            mapping = {field.get("name"): field for field in schema.fields}
            for name in header:
                fields.append(mapping.get(name, {"name": name, "type": "any"}))
            schema.fields = fields

        # Patch schema
        if self.__patch_schema:
            patch_schema = deepcopy(self.__patch_schema)
            fields = patch_schema.pop("fields", {})
            schema.update(patch_schema)
            for field in schema.fields:
                field.update((fields.get(field.get("name"), {})))

        # Validate schema
        # TODO: reconsider this - not perfect for transform
        if len(schema.field_names) != len(set(schema.field_names)):
            note = "Schemas with duplicate field names are not supported"
            raise exceptions.FrictionlessException(errors.SchemaError(note=note))

        # Store stats
        self.__resource.stats["fields"] = len(schema.fields)

        # Store state
        self.__sample = sample
        self.__field_positions = field_positions
        self.__sample_positions = sample_positions
        self.__header = Header(
            header,
            schema=schema,
            field_positions=field_positions,
            ignore_case=not dialect.header_case,
        )

    def __read_data_stream_infer_header(self, header_data):
        dialect = self.__resource.dialect

        # No header
        if not dialect.header:
            return [], list(range(1, len(header_data[0]) + 1))

        # Get header
        header = []
        prev_cells = {}
        for cells in header_data:
            for index, cell in enumerate(cells):
                if prev_cells.get(index) == cell:
                    continue
                prev_cells[index] = cell
                if len(header) <= index:
                    header.append(cell)
                    continue
                header[index] = dialect.header_join.join([header[index], cell])

        # Filter header
        filter_header = []
        field_positions = []
        limit = self.__resource.query.limit_fields
        offset = self.__resource.query.offset_fields or 0
        for field_position, header in enumerate(header, start=1):
            if self.__read_data_stream_pick_skip_field(field_position, header):
                if offset:
                    offset -= 1
                    continue
                filter_header.append(header)
                field_positions.append(field_position)
                if limit and limit <= len(filter_header):
                    break

        return filter_header, field_positions

    def __read_data_stream_pick_skip_field(self, field_position, header):
        match = True
        for name in ["pick", "skip"]:
            if name == "pick":
                items = self.__resource.query.pick_fields_compiled
            else:
                items = self.__resource.query.skip_fields_compiled
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

    def __read_data_stream_pick_skip_row(self, row_position, cells):
        match = True
        cell = cells[0] if cells else None
        cell = "" if cell is None else str(cell)
        for name in ["pick", "skip"]:
            if name == "pick":
                items = self.__resource.query.pick_rows_compiled
            else:
                items = self.__resource.query.skip_rows_compiled
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

    def __read_data_stream_filter_data(self, cells, field_positions):
        if self.__resource.query.is_field_filtering:
            result = []
            for field_position, cell in enumerate(cells, start=1):
                if field_position in field_positions:
                    result.append(cell)
            return result
        return cells

    def __read_data_stream_raise_closed(self):
        if not self.__data_stream:
            note = 'the table has not been opened by "table.open()"'
            raise exceptions.FrictionlessException(errors.Error(note=note))

    def read_rows(self):
        """Read row stream into memory

        Returns:
            Row[][]: table rows
        """
        self.__read_row_stream_raise_closed()
        return list(self.__row_stream)

    def __read_row_stream(self):
        return self.__read_row_stream_create()

    def __read_row_stream_create(self):
        schema = self.schema

        # Handle header errors
        if not self.header.valid:
            error = self.header.errors[0]
            if self.__resource.onerror == "warn":
                warnings.warn(error.message, UserWarning)
            elif self.__resource.onerror == "raise":
                raise exceptions.FrictionlessException(error)

        # Create state
        memory_unique = {}
        memory_primary = {}
        foreign_groups = []
        for field in self.schema.fields:
            if field.constraints.get("unique"):
                memory_unique[field.name] = {}
        if self.__lookup:
            for fk in self.schema.foreign_keys:
                group = {}
                group["sourceName"] = fk["reference"]["resource"]
                group["sourceKey"] = tuple(fk["reference"]["fields"])
                group["targetKey"] = tuple(fk["fields"])
                foreign_groups.append(group)

        # Stream rows
        for cells in self.__data_stream:

            # Create row
            row = Row(
                cells,
                schema=self.__resource.schema,
                field_positions=self.__field_positions,
                row_position=self.__row_position,
                row_number=self.__resource.stats["rows"],
            )

            # Unique Error
            if memory_unique:
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
            if schema.primary_key:
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
            if foreign_groups:
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
            if not row.valid:
                error = row.errors[0]
                if self.__resource.onerror == "warn":
                    warnings.warn(error.message, UserWarning)
                elif self.__resource.onerror == "raise":
                    raise exceptions.FrictionlessException(error)

            # Stream row
            yield row

    def __read_row_stream_raise_closed(self):
        if not self.__row_stream:
            note = 'the table has not been opened by "table.open()"'
            raise exceptions.FrictionlessException(errors.Error(note=note))

    # Write

    # NOTE: implement proper usage of loaders (e.g. write to s3)
    # NOTE: can we rebase on source/target resources instead of read_row_stream?
    def write(
        self,
        target=None,
        *,
        scheme=None,
        format=None,
        hashing=None,
        encoding=None,
        compression=None,
        compression_path=None,
        control=None,
        dialect=None,
    ):
        """Write the table to the target

        Parameters:
            target (str): target path
            **options: subset of Table's constructor options
        """

        # Create file
        resource = Resource.from_source(
            target,
            scheme=scheme,
            format=format,
            hashing=hashing,
            encoding=encoding,
            compression=compression,
            compression_path=compression_path,
            control=control,
            dialect=dialect,
            schema=self.schema,
            trusted=True,
        )

        # Write file
        read_row_stream = self.__write_row_stream_create
        parser = system.create_parser(resource)
        parser.write(read_row_stream)
        return resource.source

    def __write_row_stream_create(self):
        if self.__row_position:
            self.open()
        return self.row_stream
