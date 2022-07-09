# type: ignore
from __future__ import annotations
import os
import json
import petl
import warnings
from pathlib import Path
from copy import deepcopy
from collections.abc import Mapping
from typing import TYPE_CHECKING, Optional, Union, List, Any
from ..exception import FrictionlessException
from ..table import Header, Row
from ..schema import Schema
from ..detector import Detector
from ..metadata import Metadata
from ..checklist import Checklist
from ..pipeline import Pipeline
from ..dialect import Dialect, Control
from ..system import system
from .. import settings
from .. import helpers
from .. import errors
from .. import fields
from . import methods


if TYPE_CHECKING:
    from ..package import Package
    from ..interfaces import IDescriptorSource, IOnerror


class Resource(Metadata):
    """Resource representation.

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

    """

    analyze = methods.analyze
    describe = methods.describe
    extract = methods.extract
    validate = methods.validate  # type: ignore
    transform = methods.transform

    def __init__(
        self,
        source: Optional[Any] = None,
        *,
        # Standard
        name: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        profiles: List[str] = [],
        licenses: List[dict] = [],
        sources: List[dict] = [],
        path: Optional[str] = None,
        data: Optional[Any] = None,
        type: Optional[str] = None,
        scheme: Optional[str] = None,
        format: Optional[str] = None,
        hashing: Optional[str] = None,
        encoding: Optional[str] = None,
        mediatype: Optional[str] = None,
        compression: Optional[str] = None,
        extrapaths: List[str] = [],
        innerpath: Optional[str] = None,
        dialect: Optional[Union[Dialect, str]] = None,
        schema: Optional[Union[Schema, str]] = None,
        checklist: Optional[Union[Checklist, str]] = None,
        pipeline: Optional[Union[Pipeline, str]] = None,
        stats: dict = {},
        # Software
        basepath: Optional[str] = None,
        onerror: Optional[IOnerror] = None,
        trusted: Optional[bool] = None,
        detector: Optional[Detector] = None,
        package: Optional[Package] = None,
        control: Optional[Control] = None,
    ):

        # Store state
        self.name = name
        self.title = title
        self.description = description
        self.profiles = profiles.copy()
        self.licenses = licenses.copy()
        self.sources = sources.copy()
        self.type = type
        self.path = path
        self.data = data
        self.scheme = scheme
        self.format = format
        self.hashing = hashing
        self.encoding = encoding
        self.mediatype = mediatype
        self.compression = compression
        self.extrapaths = extrapaths.copy()
        self.innerpath = innerpath
        self.stats = stats.copy()
        self.package = package

        # Store dereferenced state
        self.__dialect = dialect
        self.__control = control
        self.__schema = schema
        self.__checklist = checklist
        self.__pipeline = pipeline

        # Store inherited state
        self.__basepath = basepath
        self.__onerror = onerror
        self.__trusted = trusted
        self.__detector = detector

        # Store internal state
        self.__loader = None
        self.__parser = None
        self.__sample = None
        self.__labels = None
        self.__fragment = None
        self.__header = None
        self.__lookup = None
        self.__row_stream = None

        # Handled by the create hook
        assert source is None

    @classmethod
    def __create__(cls, source: Optional[Any] = None, **options):
        if source is not None:

            # Path
            if isinstance(source, Path):
                source = str(source)

            # Mapping
            elif isinstance(source, Mapping):
                source = {key: value for key, value in source.items()}

            # Descriptor
            if helpers.is_descriptor_source(source):
                return Resource.from_descriptor(source, **options)

            # Path/data
            options["path" if isinstance(source, str) else "data"] = source
            return Resource(**options)

    # TODO: maybe it's possible to do type narrowing here?
    def __enter__(self):
        if self.closed:
            self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    # TODO: iter cell stream to be PETL-compatible?
    def __iter__(self):
        with helpers.ensure_open(self):
            # TODO: rebase on Inferred/OpenResource?
            # (here and in other places like this)
            assert self.__row_stream
            yield from self.__row_stream

    # State

    name: Optional[str]
    """
    Resource name according to the specs.
    It should be a slugified name of the resource.
    """

    title: Optional[str]
    """
    Resource title according to the specs
    It should a human-oriented title of the resource.
    """

    description: Optional[str]
    """
    Resource description according to the specs
    It should a human-oriented description of the resource.
    """

    profiles: List[str]
    """
    Strings identifying the profile of this descriptor.
    For example, `tabular-data-resource`.
    """

    licenses: List[dict]
    """
    The license(s) under which the resource is provided.
    If omitted it's considered the same as the package's licenses.
    """

    sources: List[dict]
    """
    The raw sources for this data resource.
    It MUST be an array of Source objects.
    Each Source object MUST have a title and
    MAY have path and/or email properties.
    """

    type: Optional[str]
    """
    Type of the data e.g. "table"
    """

    path: Optional[str]
    """
    Path to data source
    """

    data: Optional[Any]
    """
    Inline data source
    """

    scheme: Optional[str]
    """
    Scheme for loading the file (file, http, ...).
    If not set, it'll be inferred from `source`.
    """

    format: Optional[str]
    """
    File source's format (csv, xls, ...).
    If not set, it'll be inferred from `source`.
    """

    hashing: Optional[str]
    """
    An algorithm to hash data.
    It defaults to 'md5'.
    """

    encoding: Optional[str]
    """
    Source encoding.
    If not set, it'll be inferred from `source`.
    """

    mediatype: Optional[str]
    """
    Mediatype/mimetype of the resource e.g. “text/csv”,
    or “application/vnd.ms-excel”.  Mediatypes are maintained by the
    Internet Assigned Numbers Authority (IANA) in a media type registry.
    """

    compression: Optional[str]
    """
    Source file compression (zip, ...).
    If not set, it'll be inferred from `source`.
    """

    extrapaths: List[str]
    """
    List of paths to concatenate to the main path.
    It's used for multipart resources.
    """

    innerpath: Optional[str]
    """
    Path within the compressed file.
    It defaults to the first file in the archive (if the source is an archive).
    """

    stats: dict
    """
    Stats dictionary.
    A dict with the following possible properties: hash, bytes, fields, rows.
    """

    package: Optional[Package]
    """
    Parental to this resource package.
    For more information, please check the Package documentation.
    """

    # Props

    @property
    def dialect(self) -> Dialect:
        """
        File Dialect object.
        For more information, please check the Dialect documentation.
        """
        if self.__dialect is None:
            self.__dialect = Dialect()
            if self.__control:
                self.__dialect.set_control(self.__control)
        elif isinstance(self.__dialect, str):
            path = os.path.join(self.basepath, self.__dialect)
            self.__dialect = Dialect.from_descriptor(path)
        return self.__dialect

    @dialect.setter
    def dialect(self, value: Union[Dialect, str]):
        self.__dialect = value

    @property
    def schema(self) -> Optional[Schema]:
        """
        Table Schema object.
        For more information, please check the Schema documentation.
        """
        if isinstance(self.__schema, str):
            path = os.path.join(self.basepath, self.__schema)
            self.__schema = Schema.from_descriptor(path)
        return self.__schema

    @schema.setter
    def schema(self, value: Optional[Union[Schema, str]]):
        self.__schema = value

    @property
    def checklist(self) -> Optional[Checklist]:
        """
        Checklist object.
        For more information, please check the Checklist documentation.
        """
        if isinstance(self.__checklist, str):
            path = os.path.join(self.basepath, self.__checklist)
            self.__checklist = Checklist.from_descriptor(path)
        return self.__checklist

    @checklist.setter
    def checklist(self, value: Optional[Union[Checklist, str]]):
        self.__checklist = value

    @property
    def pipeline(self) -> Optional[Pipeline]:
        """
        Pipeline object.
        For more information, please check the Pipeline documentation.
        """
        if isinstance(self.__pipeline, str):
            path = os.path.join(self.basepath, self.__pipeline)
            self.__pipeline = Pipeline.from_descriptor(path)
        return self.__pipeline

    @pipeline.setter
    def pipeline(self, value: Optional[Union[Pipeline, str]]):
        self.__pipeline = value

    @property
    def basepath(self) -> str:
        """
        A basepath of the resource
        The fullpath of the resource is joined `basepath` and /path`
        """
        if self.__basepath is not None:
            return self.__basepath
        elif self.package:
            return self.package.basepath
        return settings.DEFAULT_BASEPATH

    @basepath.setter
    def basepath(self, value: str):
        self.__basepath = value

    @property
    def onerror(self) -> IOnerror:
        """
        Behaviour if there is an error.
        It defaults to 'ignore'. The default mode will ignore all errors
        on resource level and they should be handled by the user
        being available in Header and Row objects.
        """
        if self.__onerror is not None:
            return self.__onerror  # type: ignore
        elif self.package:
            return self.package.onerror
        return settings.DEFAULT_ONERROR

    @onerror.setter
    def onerror(self, value: IOnerror):
        self.__onerror = value

    @property
    def trusted(self) -> bool:
        """
        Don't raise an exception on unsafe paths.
        A path provided as a part of the descriptor considered unsafe
        if there are path traversing or the path is absolute.
        A path provided as `source` or `path` is alway trusted.
        """
        if self.__trusted is not None:
            return self.__trusted
        elif self.package:
            return self.package.trusted
        return settings.DEFAULT_TRUSTED

    @trusted.setter
    def trusted(self, value: bool):
        self.__trusted = value

    @property
    def detector(self) -> Detector:
        """
        Resource detector.
        For more information, please check the Detector documentation.
        """
        if self.__detector is not None:
            return self.__detector
        elif self.package:
            return self.package.detector
        self.__detector = Detector()
        return self.__detector

    @detector.setter
    def detector(self, value: Detector):
        self.__detector = value

    @property
    def description_html(self) -> str:
        """Description in HTML"""
        return helpers.md_to_html(self.description or "")

    @property
    def description_text(self) -> str:
        """Description in Text"""
        return helpers.html_to_text(self.description_html or "")

    @property
    def fullpath(self) -> Optional[str]:
        """Full path of the resource"""
        if self.path:
            return helpers.join_path(self.basepath, self.path)

    # TODO: add asteriks for user/pass in url
    @property
    def place(self) -> str:
        """Stringified resource location"""
        if self.data:
            return "<memory>"
        elif self.extrapaths:
            return f"{self.path} (multipart)"
        elif self.innerpath:
            return f"{self.path} -> {self.innerpath}"
        elif self.path:
            return self.path
        return ""

    @property
    def memory(self) -> bool:
        """Whether resource is not path based"""
        return self.data is not None

    @property
    def remote(self) -> bool:
        """Whether resource is remote"""
        return helpers.is_remote_path(self.basepath or self.path)

    @property
    def multipart(self) -> bool:
        """Whether resource is multipart"""
        return not self.memory and bool(self.extrapaths)

    @property
    def tabular(self) -> bool:
        """Whether resource is tabular"""
        return self.type == "table"

    @property
    def buffer(self):
        """File's bytes used as a sample

        These buffer bytes are used to infer characteristics of the
        source file (e.g. encoding, ...).
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

    # Infer

    def infer(self, *, sample=True, stats=False):
        """Infer metadata

        Parameters:
            sample? (bool): open file and infer from a sample (default: True)
            stats? (bool): stream file completely and infer stats
        """
        if not sample:
            self.__detect_file()
            return
        if not self.closed:
            note = "Resource.infer canot be used on a open resource"
            raise FrictionlessException(errors.ResourceError(note=note))
        with self:
            if not stats:
                # TODO: rework in v6
                self.stats = {}
                self.metadata_assigned.remove("stats")
                return
            stream = self.row_stream or self.byte_stream
            helpers.pass_through(stream)

    # Open/Close

    def open(self, *, as_file=False):
        """Open the resource as "io.open" does"""

        # Prepare
        self.close()
        self.__detect_file()

        # Open
        try:

            # Table
            if self.type == "table" and not as_file:
                self.__parser = system.create_parser(self)
                self.__parser.open()
                self.__detect_dialect()
                self.__detect_schema()
                self.__header = self.__read_header()
                self.__lookup = self.__read_lookup()
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

    # Detect

    # TODO: enable validation?
    def __detect_file(self):

        # Detect
        self.detector.detect_resource(self)
        system.detect_resource(self)

        # Validate
        #  if not self.metadata_valid:
        #  raise FrictionlessException(self.metadata_errors[0])

    def __detect_dialect(self):

        # Detect
        self.__sample = self.__parser.sample  # type: ignore
        dialect = self.detector.detect_dialect(self.__sample, dialect=self.dialect)
        if dialect:
            self.dialect = dialect

        # Validate
        if not self.dialect.metadata_valid:
            raise FrictionlessException(self.dialect.metadata_errors[0])

    def __detect_schema(self):

        # Detect
        self.__labels = self.dialect.read_labels(self.sample)
        self.__fragment = self.dialect.read_fragment(self.sample)
        field_candidates = system.create_field_candidates()
        schema = self.detector.detect_schema(
            self.__fragment,
            labels=self.__labels,
            schema=self.schema,
            field_candidates=field_candidates,
        )

        # Process
        # TODO: review
        if schema:
            if not self.schema or self.schema.to_descriptor() != schema.to_descriptor():
                self.schema = schema
        self.stats["fields"] = len(schema.fields)
        # NOTE: review whether it's a proper place for this fallback to data resource
        if not schema:
            self.profile = "data-resource"

        # Validate
        if not self.schema.metadata_valid:
            raise FrictionlessException(self.schema.metadata_errors[0])

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
            text = self.read_text(size=size)
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

    def __read_header(self):

        # Create header
        header = Header(
            self.__labels,
            fields=self.schema.fields,
            row_numbers=self.dialect.header_rows,
            ignore_case=not self.dialect.header_case,
        )

        # Handle errors
        if not header.valid:
            error = header.errors[0]
            if self.onerror == "warn":
                warnings.warn(error.message, UserWarning)
            elif self.onerror == "raise":
                raise FrictionlessException(error)

        return header

    # TODO: add lookup to interfaces
    def __read_lookup(self) -> dict:
        """Detect lookup from resource

        Parameters:
            resource (Resource): tabular resource

        Returns:
            dict: lookup
        """
        lookup = {}
        for fk in self.schema.foreign_keys:

            # Prepare source
            source_name = fk["reference"]["resource"]
            source_key = tuple(fk["reference"]["fields"])
            if source_name != "" and not self.package:
                continue
            if source_name:
                if not self.package.has_resource(source_name):
                    note = f'Failed to handle a foreign key for resource "{self.name}" as resource "{source_name}" does not exist'
                    raise FrictionlessException(errors.ResourceError(note=note))
                source_res = self.package.get_resource(source_name)
            else:
                source_res = self.to_copy()
            if source_res.schema:
                source_res.schema.foreign_keys = []

            # Prepare lookup
            lookup.setdefault(source_name, {})
            if source_key in lookup[source_name]:
                continue
            lookup[source_name][source_key] = set()
            if not source_res:
                continue
            with source_res:
                for row in source_res.row_stream:  # type: ignore
                    cells = tuple(row.get(field_name) for field_name in source_key)
                    if set(cells) == {None}:
                        continue
                    lookup[source_name][source_key].add(cells)

        return lookup

    def __read_row_stream(self):

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
            field_info["mapping"][field.name] = (field, field_number)

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
            self.__parser.list_stream
        )

        # Create row stream
        def row_stream():
            row_count = 0
            for row_number, cells in enumerated_content_stream:
                row_count += 1

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
                        group_lookup = self.__lookup.get(group["sourceName"])
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

            # Update stats
            self.stats["rows"] = row_count

        # Return row stream
        return row_stream()

    # Write

    # TODO: review this method
    def write(self, target=None, **options):
        """Write this resource to the target resource

        Parameters:
            target (any|Resource): target or target resource instance
            **options (dict): Resource constructor options
        """
        native = isinstance(target, Resource)
        target = target if native else Resource(target, **options)
        target.infer(sample=False)
        parser = system.create_parser(target)
        parser.write_row_stream(self.to_copy())
        return target

    # Convert

    # TODO: review
    def to_copy(self, **options):
        """Create a copy from the resource

        Returns
            Resource: resource copy
        """
        return super().to_copy(
            data=self.data,
            basepath=self.basepath,
            onerror=self.onerror,
            trusted=self.trusted,
            detector=self.detector,
            package=self.package,
            # TODO: rework with dialect rework
            control=self.__control,
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

    metadata_Error = errors.ResourceError
    metadata_profile = deepcopy(settings.RESOURCE_PROFILE)
    metadata_profile["properties"].pop("schema")
    # TODO: move to assets?
    metadata_profile["properties"]["compression"] = {}
    metadata_profile["properties"]["extrapaths"] = {}
    metadata_profile["properties"]["innerpath"] = {}
    metadata_profile["properties"]["dialect"] = {"type": ["string", "object"]}
    metadata_profile["properties"]["schema"] = {"type": ["string", "object"]}
    metadata_profile["properties"]["checklist"] = {"type": ["string", "object"]}
    metadata_profile["properties"]["pipeline"] = {"type": ["string", "object"]}
    metadata_profile["properties"]["stats"] = {"type": "object"}

    @classmethod
    def metadata_properties(cls):
        return super().metadata_properties(
            dialect=Dialect,
            schema=Schema,
            checklist=Checklist,
            pipeline=Pipeline,
        )

    @classmethod
    def metadata_import(cls, descriptor: IDescriptorSource, **options):
        options.setdefault("trusted", False)
        if isinstance(descriptor, str):
            options.setdefault("basepath", helpers.parse_basepath(descriptor))
        descriptor = super().metadata_normalize(descriptor)

        # Url (v0)
        url = descriptor.pop("url", None)
        if url is not None:
            descriptor.setdefault("path", url)

        # Path (v1)
        path = descriptor.get("path")
        if path and isinstance(path, list):
            descriptor["path"] = path[0]
            descriptor["extrapaths"] = path[1:]

        # Profile (v1)
        profile = descriptor.pop("profile", None)
        if profile == "data-resource":
            descriptor["type"] = "file"
        elif profile == "tabular-data-resource":
            descriptor["type"] = "table"
        elif profile:
            descriptor.setdefault("profiles", [])
            descriptor["profiles"].append(profile)

        # Stats (v1)
        for name in ["hash", "bytes"]:
            value = descriptor.pop(name, None)
            if value:
                if name == "hash":
                    hashing, value = helpers.parse_resource_hash(value)
                    if hashing != settings.DEFAULT_HASHING:
                        descriptor["hashing"] = hashing
                descriptor.setdefault("stats", {})
                descriptor["stats"][name] = value

        # Compression (v1.5)
        compression = descriptor.get("compression")
        if compression == "no":
            descriptor.pop("compression")

        return super().metadata_import(descriptor, **options)

    def metadata_export(self):
        descriptor = super().metadata_export()

        # Data
        if not isinstance(descriptor.get("data", []), list):
            descriptor["data"] = []

        # Path (v1)
        if system.standards_version == "v1":
            path = descriptor.get("path")
            extrapaths = descriptor.pop("extrapaths", None)
            if extrapaths:
                descriptor["path"] = []
                if path:
                    descriptor["path"].append(path)
                descriptor["path"].extend(extrapaths)

        # Profile (v1)
        if system.standards_version == "v1":
            type = descriptor.pop("type", None)
            profiles = descriptor.pop("profiles", None)
            if type == "table":
                descriptor["profile"] = "tabular-data-profile"
            elif profiles:
                descriptor["profile"] = profiles[0]

        # Stats (v1)
        if system.standards_version == "v1":
            stats = descriptor.pop("stats", None)
            if stats:
                hash = stats.get("hash")
                bytes = stats.get("bytes")
                if hash is not None:
                    descriptor["hash"] = hash
                if bytes is not None:
                    descriptor["bytes"] = bytes

        return descriptor

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Dialect
        if self.dialect:
            yield from self.dialect.metadata_errors

        # Schema
        if self.schema:
            yield from self.schema.metadata_errors

        # Checklist
        if self.checklist:
            yield from self.checklist.metadata_errors

        # Pipeline
        if self.pipeline:
            yield from self.pipeline.metadata_errors

        # Contributors/Sources
        for name in ["contributors", "sources"]:
            for item in getattr(self, name, []):
                if item.get("email"):
                    field = fields.StringField(format="email")
                    _, note = field.read_cell(item.get("email"))
                    if note:
                        note = f'property "{name}[].email" is not valid "email"'
                        yield errors.PackageError(note=note)
        # Custom
        for name in ["missingValues", "fields"]:
            if name in self.custom:
                note = f'"{name}" should be set as "schema.{name}"'
                yield errors.ResourceError(note=note)
