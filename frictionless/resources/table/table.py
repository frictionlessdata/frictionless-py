from __future__ import annotations
import os
import json
import warnings
import builtins
from typing import TYPE_CHECKING, Optional, Dict, Union, Any, List
from ...exception import FrictionlessException
from ...table import Header, Lookup, Row
from ...dialect import Dialect
from ...platform import platform
from ...resource import Resource
from ...system import system
from .analyze import analyze
from .transform import transform
from .validate import validate
from ... import settings
from ... import helpers
from ... import errors

if TYPE_CHECKING:
    from ...system import Loader, Parser
    from ...formats.sql import IOnRow, IOnProgress
    from ...interfaces import IBuffer, ISample, IFragment, ILabels
    from ...interfaces import IFilterFunction, IProcessFunction, ITabularData
    from ...interfaces import IByteStream, ITextStream, ICellStream
    from ...interfaces import ICallbackFunction
    from ...checklist import Checklist
    from ...pipeline import Pipeline
    from ...dialect import Control
    from ...table import IRowStream


class TableResource(Resource):
    type = "table"
    datatype = "table"
    tabular = True

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.__loader: Optional[Loader] = None
        self.__parser: Optional[Parser] = None
        self.__buffer: Optional[IBuffer] = None
        self.__sample: Optional[ISample] = None
        self.__labels: Optional[ILabels] = None
        self.__fragment: Optional[IFragment] = None
        self.__header: Optional[Header] = None
        self.__lookup: Optional[Lookup] = None
        self.__row_stream: Optional[IRowStream] = None

    @property
    def buffer(self) -> IBuffer:
        """File's bytes used as a sample

        These buffer bytes are used to infer characteristics of the
        source file (e.g. encoding, ...).
        """
        if self.__buffer is None:
            raise FrictionlessException("resource is not open or non binary")
        return self.__buffer

    @property
    def sample(self) -> ISample:
        """Table's lists used as sample.

        These sample rows are used to infer characteristics of the
        source file (e.g. schema, ...).

        Returns:
            list[]?: table sample
        """
        if self.__sample is None:
            raise FrictionlessException("resource is not open or non tabular")
        return self.__sample

    @property
    def labels(self) -> ILabels:
        """
        Returns:
            str[]?: table labels
        """
        if self.__labels is None:
            raise FrictionlessException("resource is not open or non tabular")
        return self.__labels

    @property
    def fragment(self) -> IFragment:
        """Table's lists used as fragment.

        These fragment rows are used internally to infer characteristics of the
        source file (e.g. schema, ...).

        Returns:
            list[]?: table fragment
        """
        if self.__fragment is None:
            raise FrictionlessException("resource is not open or non tabular")
        return self.__fragment

    @property
    def header(self) -> Header:
        """
        Returns:
            str[]?: table header
        """
        if self.__header is None:
            raise FrictionlessException("resource is not open or non tabular")
        return self.__header

    @property
    def lookup(self) -> Lookup:
        """
        Returns:
            str[]?: table lookup
        """
        if self.__lookup is None:
            raise FrictionlessException("resource is not open or non tabular")
        return self.__lookup

    @property
    def byte_stream(self) -> IByteStream:
        """Byte stream in form of a generator

        Yields:
            gen<bytes>?: byte stream
        """
        if self.closed:
            raise FrictionlessException("resource is not open or non binary")
        if not self.__loader:
            self.__loader = system.create_loader(self)
            self.__loader.open()
        return self.__loader.byte_stream

    @property
    def text_stream(self) -> ITextStream:
        """Text stream in form of a generator

        Yields:
            gen<str[]>?: text stream
        """
        if self.closed:
            raise FrictionlessException("resource is not open or non textual")
        if not self.__loader:
            self.__loader = system.create_loader(self)
            self.__loader.open()
        return self.__loader.text_stream

    @property
    def cell_stream(self) -> ICellStream:
        """Cell stream in form of a generator

        Yields:
            gen<any[][]>?: cell stream
        """
        if self.__parser is None:
            raise FrictionlessException("resource is not open or non tabular")
        return self.__parser.cell_stream

    @property
    def row_stream(self) -> IRowStream:
        """Row stream in form of a generator of Row objects

        Yields:
            gen<Row[]>?: row stream
        """
        if self.__row_stream is None:
            raise FrictionlessException("resource is not open or non tabular")
        return self.__row_stream

    # Open/Close

    def open(self):
        """Open the resource as "io.open" does"""
        self.close()
        try:
            self.__prepare_parser()
            self.__prepare_buffer()
            self.__prepare_sample()
            self.__prepare_dialect()
            self.__prepare_labels()
            self.__prepare_fragment()
            self.__prepare_schema()
            self.__prepare_header()
            self.__prepare_lookup()
            self.__prepare_row_stream()
        except Exception:
            self.close()
            raise
        return self

    def close(self) -> None:
        """Close the resource as "filelike.close" does"""
        if self.__parser:
            self.__parser.close()
            self.__parser = None
        if self.__loader:
            self.__loader.close()
            self.__loader = None

    @property
    def closed(self) -> bool:
        """Whether the table is closed

        Returns:
            bool: if closed
        """
        return self.__parser is None and self.__loader is None

    def __prepare_loader(self):
        self.__loader = system.create_loader(self)
        self.__loader.open()

    def __prepare_buffer(self):
        if self.__parser and self.__parser.requires_loader:
            self.__buffer = self.__parser.loader.buffer
        elif self.__loader:
            self.__buffer = self.__loader.buffer

    def __prepare_parser(self):
        self.__parser = system.create_parser(self)
        self.__parser.open()

    def __prepare_sample(self):
        if self.__parser:
            self.__sample = self.__parser.sample

    def __prepare_dialect(self):
        self.metadata_assigned.add("dialect")
        self.dialect = self.detector.detect_dialect(self.sample, dialect=self.dialect)

    def __prepare_labels(self):
        self.__labels = self.dialect.read_labels(self.sample)

    def __prepare_fragment(self):
        self.__fragment = self.dialect.read_fragment(self.sample)

    def __prepare_schema(self):
        self.metadata_assigned.add("schema")
        self.schema = self.detector.detect_schema(
            self.fragment,
            labels=self.labels,
            schema=self.schema,
            field_candidates=system.detect_field_candidates(),
        )
        self.stats.fields = len(self.schema.fields)

    def __prepare_header(self):
        # Create header
        self.__header = Header(
            self.__labels,
            fields=self.schema.fields,
            row_numbers=self.dialect.header_rows,
            ignore_case=not self.dialect.header_case,
        )

        # Handle errors
        if not self.header.valid:
            error = self.header.errors[0]
            if system.onerror == "warn":
                warnings.warn(error.message, UserWarning)
            elif system.onerror == "raise":
                raise FrictionlessException(error)

    def __prepare_lookup(self):
        self.__lookup = Lookup()
        for fk in self.schema.foreign_keys:
            # Prepare source
            source_name = fk["reference"]["resource"]
            source_key = tuple(fk["reference"]["fields"])
            if source_name != "" and not self.package:
                continue
            if source_name:
                if not self.package:
                    note = 'package is required for FK: "{fk}"'
                    raise FrictionlessException(errors.ResourceError(note=note))
                if not self.package.has_resource(source_name):
                    note = f'failed to handle a foreign key for resource "{self.name}" as resource "{source_name}" does not exist'
                    raise FrictionlessException(errors.ResourceError(note=note))
                source_res = self.package.get_resource(source_name)
            else:
                source_res = self.to_copy()
            if source_res.schema:
                source_res.schema.foreign_keys = []

            # Prepare lookup
            self.__lookup.setdefault(source_name, {})
            if source_key in self.__lookup[source_name]:
                continue
            self.__lookup[source_name][source_key] = set()
            if not source_res:
                continue
            with source_res:
                for row in source_res.row_stream:  # type: ignore
                    cells = tuple(row.get(field_name) for field_name in source_key)
                    if set(cells) == {None}:
                        continue
                    self.__lookup[source_name][source_key].add(cells)

    def __prepare_row_stream(self):
        # TODO: we need to rework this field_info / row code
        # During row streaming we crate a field info structure
        # This structure is optimized and detached version of schema.fields
        # We create all data structures in-advance to share them between rows

        # Create field info
        field_number = 0
        field_info = {"names": [], "objects": [], "mapping": {}}
        for field in self.schema.fields:
            field_number += 1
            field_info["names"].append(field.name)
            field_info["objects"].append(field.to_copy())
            field_info["mapping"][field.name] = (
                field,
                field_number,
                field.create_cell_reader(),
                field.create_cell_writer(),
            )

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

        # Create content stream
        enumerated_content_stream = self.dialect.read_enumerated_content_stream(
            self.cell_stream
        )

        # Create row stream
        def row_stream():
            self.stats.rows = 0
            for row_number, cells in enumerated_content_stream:
                self.stats.rows += 1

                # Create row
                row = Row(
                    cells,
                    field_info=field_info,
                    row_number=row_number,
                )

                # Unique Error
                if is_integrity and memory_unique:
                    for field_name in memory_unique.keys():
                        cell = row[field_name]
                        if cell is not None:
                            match = memory_unique[field_name].get(cell)
                            memory_unique[field_name][cell] = row.row_number
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
                        memory_primary[cells] = row.row_number
                        if match:
                            if match:
                                note = "the same as in the row at position %s" % match
                                error = errors.PrimaryKeyError.from_row(row, note=note)
                                row.errors.append(error)

                # Foreign Key Error
                if is_integrity and foreign_groups:
                    for group in foreign_groups:
                        group_lookup = self.lookup.get(group["sourceName"])
                        if group_lookup:
                            cells = tuple(row[name] for name in group["targetKey"])
                            if set(cells) == {None}:
                                continue
                            match = cells in group_lookup.get(group["sourceKey"], set())
                            if not match:
                                note = (
                                    'for "%s": values "%s" not found in the lookup table "%s" as "%s"'
                                    % (
                                        ", ".join(group["targetKey"]),
                                        ", ".join(str(d) for d in cells),
                                        group["sourceName"],
                                        ", ".join(group["sourceKey"]),
                                    )
                                )

                                error = errors.ForeignKeyError.from_row(
                                    row,
                                    note=note,
                                    field_names=list(group["targetKey"]),
                                    field_values=list(cells),
                                    reference_name=group["sourceName"],
                                    reference_field_names=list(group["sourceKey"]),
                                )
                                row.errors.append(error)

                # Handle errors
                if system.onerror != "ignore":
                    if not row.valid:
                        error = row.errors[0]
                        if system.onerror == "raise":
                            raise FrictionlessException(error)
                        warnings.warn(error.message, UserWarning)

                # Yield row
                yield row

        # Crreate row stream
        self.__row_stream = row_stream()

    # TODO: open as a file?
    def read_bytes(self, *, size: Optional[int] = None) -> bytes:
        """Read bytes into memory

        Returns:
            any[][]: resource bytes
        """
        if self.memory:
            return b""
        with helpers.ensure_open(self):
            # Without size we need to read chunk by chunk because read1 doesn't return
            # the full contents by default (just an arbitrary amount of bytes)
            # and we use read1 as it includes stats calculation (system.loader)
            if not size:
                buffer = b""
                while True:
                    chunk = self.byte_stream.read1()  # type: ignore
                    buffer += chunk
                    if not chunk:
                        break
                return buffer
            return self.byte_stream.read1(size)  # type: ignore

    def read_text(self, *, size: Optional[int] = None) -> str:
        """Read text into memory

        Returns:
            str: resource text
        """
        if self.memory:
            return ""
        with helpers.ensure_open(self):
            return self.text_stream.read(size)  # type: ignore

    # TODO: support yaml?
    def read_data(self, *, size: Optional[int] = None) -> Any:
        """Read data into memory

        Returns:
            any: resource data
        """
        if self.data is not None:
            return self.data
        with helpers.ensure_open(self):
            text = self.read_text(size=size)
            data = json.loads(text)
            return data

    def read_cells(self, *, size: Optional[int] = None) -> List[List[Any]]:
        """Read lists into memory

        Returns:
            any[][]: table lists
        """
        with helpers.ensure_open(self):
            result = []
            for cells in self.cell_stream:
                result.append(cells)
                if size and len(result) >= size:
                    break
            return result

    def read_rows(self, *, size=None) -> List[Row]:
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

    # Infer

    # TODO: allow cherry-picking stats for adding to a descriptor
    def infer(self, *, stats: bool = False) -> None:
        """Infer metadata

        Parameters:
            stats: stream file completely and infer stats
        """
        if not self.closed:
            note = "Resource.infer canot be used on a open resource"
            raise FrictionlessException(errors.ResourceError(note=note))
        with self:
            if not stats:
                return
            helpers.pass_through(self.row_stream)
            self.hash = f"sha256:{self.stats.sha256}"
            self.bytes = self.stats.bytes
            self.fields = self.stats.fields
            self.rows = self.stats.rows

    # Analyze

    def analyze(self, *, detailed=False) -> Dict:
        """Analyze the resource

        This feature is currently experimental, and its API may change
        without warning.

        Parameters:
            detailed? (bool): detailed analysis

        Returns:
            dict: resource analysis

        """
        return analyze(self, detailed=detailed)

    # Convert

    def convert(
        self,
        to_path: str,
        to_format: Optional[str] = None,
        to_dialect: Optional[Union[Dialect, str]] = None,
    ) -> str:
        dialect = to_dialect or Dialect()
        target = TableResource(path=to_path, format=to_format, dialect=dialect)
        if os.path.exists(to_path):
            note = f'Cannot convert to the existent path "{to_path}"'
            raise FrictionlessException(note)
        self.write(target)
        return to_path

    # Extract

    def extract(
        self,
        *,
        name: Optional[str] = None,
        filter: Optional[IFilterFunction] = None,
        process: Optional[IProcessFunction] = None,
        limit_rows: Optional[int] = None,
    ) -> ITabularData:
        if not process:
            process = lambda row: row.to_dict()
        data = self.read_rows(size=limit_rows)
        data = builtins.filter(filter, data) if filter else data
        data = (process(row) for row in data) if process else data
        return {name or self.name: list(data)}

    # Index

    def index(
        self,
        database_url: str,
        *,
        name: Optional[str] = None,
        fast: bool = False,
        on_row: Optional[IOnRow] = None,
        on_progress: Optional[IOnProgress] = None,
        use_fallback: bool = False,
        qsv_path: Optional[str] = None,
    ) -> List[str]:
        name = name or self.name
        indexer = platform.frictionless_formats.sql.SqlIndexer(
            resource=self,
            database_url=database_url,
            table_name=name,
            fast=fast,
            on_row=on_row,
            on_progress=on_progress,
            use_fallback=use_fallback,
            qsv_path=qsv_path,
        )
        indexer.index()
        return [name]

    # Transform

    def transform(self, pipeline: Pipeline):
        return transform(self, pipeline)

    # Validate

    def validate(
        self,
        checklist: Optional[Checklist] = None,
        *,
        name: Optional[str] = None,
        on_row: Optional[ICallbackFunction] = None,
        parallel: bool = False,
        limit_rows: Optional[int] = None,
        limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    ):
        return validate(
            self,
            checklist,
            on_row=on_row,
            limit_rows=limit_rows,
            limit_errors=limit_errors,
        )

    # Write

    def write(
        self,
        target: Optional[Union[Resource, Any]] = None,
        *,
        control: Optional[Control] = None,
        **options,
    ) -> Resource:
        """Write this resource to the target resource

        Parameters:
            target (Resource|Any): target or target resource instance
            **options (dict): Resource constructor options
        """
        resource = target
        if not isinstance(resource, Resource):
            resource = Resource(target, control=control, **options)
        parser = system.create_parser(resource)
        parser.write_row_stream(self)
        return resource

    # Export

    def to_view(self, type="look", **options):
        """Create a view from the resource

        See PETL's docs for more information:
        https://platform.petl.readthedocs.io/en/stable/util.html#visualising-tables

        Parameters:
            type (look|lookall|see|display|displayall): view's type
            **options (dict): options to be passed to PETL

        Returns
            str: resource's view
        """
        assert type in ["look", "lookall", "see", "display", "displayall"]
        view = str(getattr(self.to_petl(normalize=True), type)(**options))
        return view

    def to_inline(self, *, dialect=None):
        """Helper to export resource as an inline data"""
        dialect = dialect or Dialect()
        target = self.write(Resource(format="inline", dialect=dialect))  # type: ignore
        return target.data

    def to_pandas(self, *, dialect=None):
        """Helper to export resource as an Pandas dataframe"""
        dialect = dialect or Dialect()
        target = self.write(Resource(format="pandas", dialect=dialect))  # type: ignore
        return target.data

    def to_snap(self, *, json=False):
        """Create a snapshot from the resource

        Parameters:
            json (bool): make data types compatible with JSON format

        Returns
            list: resource's data
        """
        snap = []
        with helpers.ensure_open(self):
            snap.append(self.header.to_list())
            for row in self.row_stream:
                snap.append(row.to_list(json=json))
        return snap

    @staticmethod
    def from_petl(view, **options):
        """Create a resource from PETL view"""
        return TableResource(data=view, **options)

    def to_petl(self, normalize=False):
        """Export resource as a PETL table"""
        resource = self

        # Define view
        class ResourceView(platform.petl.Table):
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
