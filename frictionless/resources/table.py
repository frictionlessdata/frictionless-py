from __future__ import annotations

import builtins
import os
import warnings
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from frictionless.schema.field import Field

from .. import errors, helpers, settings
from ..analyzer import Analyzer
from ..dialect import Dialect
from ..exception import FrictionlessException
from ..indexer import Indexer
from ..platform import platform
from ..resource import Resource
from ..system import system
from ..table import Header, Lookup, Row, Table
from ..transformer import Transformer
from ..validator import Validator

if TYPE_CHECKING:
    from .. import types
    from ..checklist import Checklist
    from ..indexer import IOnProgress, IOnRow
    from ..pipeline import Pipeline
    from ..system import Loader, Parser
    from ..table import IRowStream


class TableResource(Resource):
    type = "table"
    datatype = "table"
    tabular = True

    def __attrs_post_init__(self):
        self.__loader: Optional[Loader] = None
        self.__parser: Optional[Parser] = None
        self.__buffer: Optional[types.IBuffer] = None
        self.__sample: Optional[types.ISample] = None
        self.__labels: Optional[types.ILabels] = None
        self.__fragment: Optional[types.IFragment] = None
        self.__header: Optional[Header] = None
        self.__lookup: Optional[Lookup] = None
        self.__row_stream: Optional[IRowStream] = None
        super().__attrs_post_init__()

    # Open/Close

    @property
    def buffer(self) -> types.IBuffer:
        """File's bytes used as a sample

        These buffer bytes are used to infer characteristics of the
        source file (e.g. encoding, ...).
        """
        if self.__buffer is None:
            raise FrictionlessException("resource is not open or non binary")
        return self.__buffer

    @property
    def sample(self) -> types.ISample:
        """Table's lists used as sample.

        These sample rows are used to infer characteristics of the
        source file (e.g. schema, ...).

        Returns:
            list[]?: table sample
        """
        if self.__sample is None:
            raise FrictionlessException("resource is not open")
        return self.__sample

    @property
    def labels(self) -> types.ILabels:
        """
        Returns:
            str[]?: table labels
        """
        if self.__labels is None:
            raise FrictionlessException("resource is not open")
        return self.__labels

    @property
    def fragment(self) -> types.IFragment:
        """Table's lists used as fragment.

        These fragment rows are used internally to infer characteristics of the
        source file (e.g. schema, ...).

        Returns:
            list[]?: table fragment
        """
        if self.__fragment is None:
            raise FrictionlessException("resource is not open")
        return self.__fragment

    @property
    def header(self) -> Header:
        """
        Returns:
            str[]?: table header
        """
        if self.__header is None:
            raise FrictionlessException("resource is not open")
        return self.__header

    @property
    def lookup(self) -> Lookup:
        """
        Returns:
            str[]?: table lookup
        """
        if self.__lookup is None:
            raise FrictionlessException("resource is not open")
        return self.__lookup

    @property
    def cell_stream(self) -> types.ICellStream:
        """Cell stream in form of a generator

        Yields:
            gen<any[][]>?: cell stream
        """
        if self.__parser is None:
            raise FrictionlessException("resource is not open")
        return self.__parser.cell_stream

    @property
    def row_stream(self) -> IRowStream:
        """Row stream in form of a generator of Row objects

        Yields:
            gen<Row[]>?: row stream
        """
        if self.__row_stream is None:
            raise FrictionlessException("resource is not open")
        return self.__row_stream

    @property
    def closed(self) -> bool:
        """Whether the table is closed

        Returns:
            bool: if closed
        """
        return self.__parser is None

    def close(self) -> None:
        """Close the resource as "filelike.close" does"""
        if self.__parser:
            self.__parser.close()
            self.__parser = None
        if self.__loader:
            self.__loader.close()
            self.__loader = None

    def open(self):
        """Open the resource as "io.open" does"""
        self.close()
        try:
            self.__open_parser()
            self.__open_buffer()
            self.__open_sample()
            self.__open_dialect()
            self.__open_labels()
            self.__open_fragment()
            self.__open_schema()
            self.__open_header()
            self.__open_lookup()
            self.__open_row_stream()
        except Exception:
            self.close()
            raise
        return self

    def __open_parser(self):
        self.__parser = system.create_parser(self)
        self.__parser.open()

    def __open_buffer(self):
        if self.__parser and self.__parser.requires_loader:
            self.__buffer = self.__parser.loader.buffer
        elif self.__loader:
            self.__buffer = self.__loader.buffer

    def __open_sample(self):
        if self.__parser:
            self.__sample = self.__parser.sample

    def __open_dialect(self):
        self.metadata_assigned.add("dialect")
        self.dialect = self.detector.detect_dialect(self.sample, dialect=self.dialect)

    def __open_labels(self):
        self.__labels = self.dialect.read_labels(self.sample)

    def __open_fragment(self):
        self.__fragment = self.dialect.read_fragment(self.sample)

    def __open_schema(self):
        self.metadata_assigned.add("schema")
        self.schema = self.detector.detect_schema(
            self.fragment,
            labels=self.labels,
            schema=self.schema,
            field_candidates=system.detect_field_candidates(),
            header_case=self.dialect.header_case,
        )
        self.stats.fields = len(self.schema.fields)

    def __open_header(self):
        assert self.__labels is not None

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

    def __open_lookup(self):
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
                    cells = tuple(row.get(field_name) for field_name in source_key)  # type: ignore
                    if set(cells) == {None}:  # type: ignore
                        continue
                    self.__lookup[source_name][source_key].add(cells)

    def __open_row_stream(self):
        # TODO: we need to rework this field_info / row code
        # During row streaming we create a field info structure
        # This structure is optimized and detached version of schema.fields
        # We create all data structures in-advance to share them between rows

        # Create field info
        field_number = 0
        field_info: Dict[str, Any] = {"names": [], "objects": [], "mapping": {}}
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
        memory_unique: Dict[str, Any] = {}
        memory_primary: Dict[Tuple[Any], Any] = {}
        foreign_groups: List[Any] = []
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
                    try:
                        cells = self.primary_key_cells(row, self.dialect.header_case)
                    except KeyError:
                        # Row does not have primary_key as label
                        # There should already be a missing-label error in
                        # in self.header corresponding to the schema primary key
                        assert not self.header.valid
                    else:
                        if set(cells) == {None}:
                            note = 'cells composing the primary keys are all "None"'
                            error = errors.PrimaryKeyError.from_row(row, note=note)
                            row.errors.append(error)
                        else:
                            match = memory_primary.get(cells)
                            memory_primary[cells] = row.row_number
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

        if self.detector.schema_sync:
            # Missing required labels are not included in the
            # field_info parameter used for row creation
            for field in self.schema.fields:
                self.remove_missing_required_label_from_field_info(field, field_info)

        # Create row stream
        self.__row_stream = row_stream()

    def remove_missing_required_label_from_field_info(
        self, field: Field, field_info: Dict[str, Any]
    ):
        is_case_sensitive = self.dialect.header_case
        if self.label_is_missing(
            field.name, field_info["names"], self.labels, is_case_sensitive
        ):
            self.remove_field_from_field_info(field.name, field_info)

    @staticmethod
    def label_is_missing(
        field_name: str,
        expected_field_names: List[str],
        table_labels: types.ILabels,
        case_sensitive: bool,
    ) -> bool:
        """Check if a schema field name is missing from the TableResource
        labels.
        """
        if not case_sensitive:
            field_name = field_name.lower()
            table_labels = [label.lower() for label in table_labels]
            expected_field_names = [
                field_name.lower() for field_name in expected_field_names
            ]

        return field_name not in table_labels and field_name in expected_field_names

    @staticmethod
    def remove_field_from_field_info(field_name: str, field_info: Dict[str, Any]):
        field_index = field_info["names"].index(field_name)
        del field_info["names"][field_index]
        del field_info["objects"][field_index]
        del field_info["mapping"][field_name]

    def primary_key_cells(self, row: Row, case_sensitive: bool) -> Tuple[Any, ...]:
        """Create a tuple containg all cells from a given row associated to primary
        keys"""
        return tuple(row[label] for label in self.primary_key_labels(row, case_sensitive))

    def primary_key_labels(
        self,
        row: Row,
        case_sensitive: bool,
    ) -> List[str]:
        """Create a list of TableResource labels that are primary keys"""
        if case_sensitive:
            labels_primary_key = self.schema.primary_key
        else:
            lower_primary_key = [pk.lower() for pk in self.schema.primary_key]
            labels_primary_key = [
                label for label in row.field_names if label.lower() in lower_primary_key
            ]
        return labels_primary_key

    # Read
    def read_cells(self, *, size: Optional[int] = None) -> List[List[Any]]:
        """Read lists into memory

        Returns:
            any[][]: table lists
        """
        with helpers.ensure_open(self):
            result: List[Any] = []
            for cells in self.cell_stream:
                result.append(cells)
                if size and len(result) >= size:
                    break
            return result

    def read_rows(self, *, size: Optional[int] = None) -> List[Row]:
        """Read rows into memory

        Returns:
            Row[]: table rows
        """
        with helpers.ensure_open(self):
            rows: List[Row] = []
            for row in self.row_stream:
                rows.append(row)
                if size and len(rows) >= size:
                    break
            return rows

    # TODO: implement
    def read_table(self) -> Table:
        rows = self.read_rows()
        header = self.header
        schema = self.schema
        return Table(schema=schema, header=header, rows=rows)

    # Write

    def write_table(
        self, target: Optional[Union[Resource, Any]] = None, **options: Any
    ) -> TableResource:
        """Write this resource to the target resource

        You can pass:
        - a target resource instance (no extra options are allowed) OR
        - path and options to create a new resource.

        Parameters:
            target (Resource|Any): target path or target resource instance
            **options (dict): resource constructor options
        """
        resource = target
        if not isinstance(resource, Resource):
            resource = Resource(target, **options)
        if not isinstance(resource, TableResource):
            raise FrictionlessException("target must be a table resource")
        parser = system.create_parser(resource)
        parser.write_row_stream(self)
        return resource

    # Infer

    # TODO: allow cherry-picking stats for adding to a descriptor
    def infer(self, *, stats: bool = False) -> None:
        """Infer metadata

        Parameters:
            stats: stream file completely and infer stats
        """
        if not self.closed:
            note = "Resource.infer cannot be used on a open resource"
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

    def analyze(self, *, detailed: bool = False):
        """Analyze the resource

        This feature is currently experimental, and its API may change
        without warning.

        Parameters:
            detailed: do detailed analysis

        Returns:
            dict: resource analysis

        """
        analyzer = Analyzer()
        return analyzer.analyze_table_resource(self, detailed=detailed)

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
        filter: Optional[types.IFilterFunction] = None,
        process: Optional[types.IProcessFunction] = None,
        limit_rows: Optional[int] = None,
    ) -> types.ITabularData:
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
        with_metadata: bool = False,
        on_row: Optional[IOnRow] = None,
        on_progress: Optional[IOnProgress] = None,
        use_fallback: bool = False,
        qsv_path: Optional[str] = None,
    ) -> List[str]:
        name = name or self.name
        indexer = Indexer(
            resource=self,
            database=database_url,
            table_name=name,
            fast=fast,
            with_metadata=with_metadata,
            on_row=on_row,
            on_progress=on_progress,
            use_fallback=use_fallback,
            qsv_path=qsv_path,
        )
        indexer.index()
        return [name]

    # Transform

    def transform(self, pipeline: Pipeline):
        transformer = Transformer()
        return transformer.transform_table_resource(self, pipeline)

    # Validate

    def validate(
        self,
        checklist: Optional[Checklist] = None,
        *,
        name: Optional[str] = None,
        on_row: Optional[types.ICallbackFunction] = None,
        parallel: bool = False,
        limit_rows: Optional[int] = None,
        limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    ):
        validator = Validator()
        return validator.validate_resource(
            self,
            checklist=checklist,
            on_row=on_row,
            limit_rows=limit_rows,
            limit_errors=limit_errors,
        )

    # Export

    def to_view(self, type: str = "look", **options: Any):
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

    def to_inline(self, *, dialect: Optional[Dialect] = None):
        """Helper to export resource as an inline data"""
        dialect = dialect or Dialect()
        target = self.write(Resource(format="inline", dialect=dialect))  # type: ignore
        return target.data

    def to_pandas(self, *, dialect: Optional[Dialect] = None):
        """Helper to export resource as an Pandas dataframe"""
        dialect = dialect or Dialect()
        target = self.write(Resource(format="pandas", dialect=dialect))  # type: ignore
        return target.data

    def to_polars(self, *, dialect: Optional[Dialect] = None):
        """Helper to export resource as an Polars dataframe"""
        dialect = dialect or Dialect()
        target = self.write(Resource(format="polars", dialect=dialect))  # type: ignore
        return target.data

    def to_snap(self, *, json: bool = False):
        """Create a snapshot from the resource

        Parameters:
            json (bool): make data types compatible with JSON format

        Returns
            list: resource's data
        """
        snap: List[List[Any]] = []
        with helpers.ensure_open(self):
            snap.append(self.header.to_list())
            for row in self.row_stream:
                snap.append(row.to_list(json=json))
        return snap

    @staticmethod
    def from_petl(view: Any, **options: Any):
        """Create a resource from PETL view"""
        return TableResource(data=view, **options)

    def to_petl(self, normalize: bool = False):
        """Export resource as a PETL table"""
        resource = self.to_copy()

        # Define view
        class ResourceView(platform.petl.Table):  # type: ignore
            def __iter__(self):  # type: ignore
                with resource:
                    if normalize:
                        yield resource.schema.field_names
                        yield from (row.to_list() for row in resource.row_stream)
                        return
                    if not resource.header.missing:
                        yield resource.header.labels
                    yield from (row.cells for row in resource.row_stream)

        return ResourceView()

    # Legacy

    def write(
        self, target: Optional[Union[Resource, Any]] = None, **options: Any
    ) -> TableResource:
        return self.write_table(target, **options)
