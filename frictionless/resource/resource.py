from __future__ import annotations

import json
import warnings
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional, Union, cast

import attrs
from typing_extensions import Self

from .. import errors, fields, helpers, settings
from ..detector import Detector
from ..dialect import Control, Dialect
from ..exception import FrictionlessException
from ..metadata import Metadata
from ..platform import platform
from ..schema import Schema
from ..system import system
from ..validator import Validator
from .factory import Factory
from .stats import ResourceStats

if TYPE_CHECKING:
    from .. import types
    from ..checklist import Checklist
    from ..package import Package
    from ..report import Report
    from ..system import Loader


@attrs.define(kw_only=True, repr=False)
class Resource(Metadata, metaclass=Factory):  # type: ignore
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

    source: Optional[Any] = attrs.field(default=None, kw_only=False)
    """
    # TODO: add docs
    """

    control: Optional[Control] = None
    """
    # TODO: add docs
    """

    packagify: bool = False
    """
    # TODO: add docs
    """

    _name: Optional[str] = attrs.field(default="", alias="name")
    """
    Resource name according to the specs.
    It should be a slugified name of the resource.
    """

    type: ClassVar[str]
    """
    Type of the resource
    """

    title: Optional[str] = None
    """
    Resource title according to the specs
    It should a human-oriented title of the resource.
    """

    description: Optional[str] = None
    """
    Resource description according to the specs
    It should a human-oriented description of the resource.
    """

    homepage: Optional[str] = None
    """
    A URL for the home on the web that is related to this package.
    For example, github repository or ckan dataset address.
    """

    profile: Optional[str] = None
    """
    A fully-qualified URL that points directly to a JSON Schema
    that can be used to validate the descriptor
    """

    licenses: List[Dict[str, Any]] = attrs.field(factory=list)
    """
    The license(s) under which the resource is provided.
    If omitted it's considered the same as the package's licenses.
    """

    sources: List[Dict[str, Any]] = attrs.field(factory=list)
    """
    The raw sources for this data resource.
    It MUST be an array of Source objects.
    Each Source object MUST have a title and
    MAY have path and/or email properties.
    """

    path: Optional[str] = None
    """
    Path to data source
    """

    data: Optional[Any] = None
    """
    Inline data source
    """

    scheme: Optional[str] = None
    """
    Scheme for loading the file (file, http, ...).
    If not set, it'll be inferred from `source`.
    """

    format: Optional[str] = None
    """
    File source's format (csv, xls, ...).
    If not set, it'll be inferred from `source`.
    """

    _datatype: Optional[str] = attrs.field(default="", alias="datatype")
    """
    Frictionless Framework specific data type as "table" or "schema"
    """

    mediatype: Optional[str] = None
    """
    Mediatype/mimetype of the resource e.g. “text/csv”,
    or “application/vnd.ms-excel”.  Mediatypes are maintained by the
    Internet Assigned Numbers Authority (IANA) in a media type registry.
    """

    compression: Optional[str] = None
    """
    Source file compression (zip, ...).
    If not set, it'll be inferred from `source`.
    """

    extrapaths: List[str] = attrs.field(factory=list)
    """
    List of paths to concatenate to the main path.
    It's used for multipart resources.
    """

    innerpath: Optional[str] = None
    """
    Path within the compressed file.
    It defaults to the first file in the archive (if the source is an archive).
    """

    encoding: Optional[str] = None
    """
    Source encoding.
    If not set, it'll be inferred from `source`.
    """

    hash: Optional[str] = None
    """
    # TODO: add docs
    """

    bytes: Optional[int] = None
    """
    # TODO: add docs
    """

    fields: Optional[int] = None
    """
    # TODO: add docs
    """

    rows: Optional[int] = None
    """
    # TODO: add docs
    """

    _dialect: Union[Dialect, str] = attrs.field(factory=Dialect, alias="dialect")
    """
    # TODO: add docs
    """

    _schema: Union[Schema, str] = attrs.field(factory=Schema, alias="schema")
    """
    # TODO: add docs
    """

    _basepath: Optional[str] = attrs.field(default=None, alias="basepath")
    """
    # TODO: add docs
    """

    detector: Detector = attrs.field(factory=Detector)
    """
    File/table detector.
    For more information, please check the Detector documentation.
    """

    package: Optional[Package] = None
    """
    Parental to this resource package.
    For more information, please check the Package documentation.
    """

    stats: ResourceStats = attrs.field(init=False)
    """
    # TODO: add docs
    """

    tabular: ClassVar[bool] = False
    """
    Whether the resoruce is tabular
    """

    def __attrs_post_init__(self):
        self.name = self._name or ""
        self.datatype = self._datatype or ""
        self.stats = ResourceStats()

        # Datatype
        datatype = getattr(type(self), "datatype", None)
        if isinstance(datatype, str):
            self.datatype = datatype

        # Internal
        self.__loader: Optional[Loader] = None
        self.__buffer: Optional[types.IBuffer] = None

        # Detect resource
        system.detect_resource(self)

        # TODO: remove this defined/not-defined logic?
        # Define default state
        self.add_defined("name")
        self.add_defined("scheme")
        self.add_defined("format")
        self.add_defined("compression")
        self.add_defined("mediatype")
        self.add_defined("dialect")
        self.add_defined("stats")

        super().__attrs_post_init__()

    # TODO: shall we guarantee here that it's at the beggining for the file?
    # TODO: maybe it's possible to do type narrowing here?
    def __enter__(self):
        if self.closed:
            self.open()
        return self

    def __exit__(self, type, value, traceback):  # type: ignore
        self.close()

    @property
    def paths(self) -> List[str]:
        """All paths of the resource"""
        paths: List[str] = []
        if self.path is not None:
            paths.append(self.path)
        paths.extend(self.extrapaths)
        return paths

    @property
    def normpaths(self) -> List[str]:
        """Normalized paths of the resource"""
        normpaths: List[str] = []
        for path in self.paths:
            normpaths.append(helpers.normalize_path(path, basepath=self.basepath))
        return normpaths

    @property
    def normpath(self) -> Optional[str]:
        """Normalized path of the resource or raise if not set"""
        if self.path:
            return helpers.normalize_path(self.path, basepath=self.basepath)

    # TODO: add asteriks for user/pass in url
    @property
    def place(self) -> str:
        """Stringified resource location"""
        if self.data is not None:
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
        return helpers.is_remote_path(self.basepath or self.path or "")

    @property
    def multipart(self) -> bool:
        """Whether resource is multipart"""
        return not self.memory and bool(self.extrapaths)

    @property
    def dialect(self) -> Dialect:
        if isinstance(self._dialect, str):
            self._dialect = Dialect.from_descriptor(self._dialect, basepath=self.basepath)
        return self._dialect

    @dialect.setter
    def dialect(self, value: Union[Dialect, str]):
        self._dialect = value

    @property
    def schema(self) -> Schema:
        if isinstance(self._schema, str):
            self._schema = Schema.from_descriptor(self._schema, basepath=self.basepath)
        return self._schema

    @schema.setter
    def schema(self, value: Union[Schema, str]):
        self._schema = value

    @property
    def basepath(self) -> Optional[str]:
        """
        A basepath of the resource
        The normpath of the resource is joined `basepath` and `/path`
        """
        if self._basepath:
            return self._basepath
        if self.package:
            return self.package.basepath

    @basepath.setter
    def basepath(self, value: Optional[str]):
        self._basepath = value

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
    def byte_stream(self) -> types.IByteStream:
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
    def text_stream(self) -> types.ITextStream:
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
    def closed(self) -> bool:
        """Whether the table is closed

        Returns:
            bool: if closed
        """
        return self.__loader is None

    def close(self) -> None:
        """Close the resource as "filelike.close" does"""
        if self.__loader:
            self.__loader.close()
            self.__loader = None

    def open(self):
        """Open the resource as "io.open" does"""
        self.close()
        try:
            self.__loader = system.create_loader(self)
            self.__loader.open()
            self.__buffer = self.__loader.buffer
        except Exception:
            self.close()
            raise
        return self

    # Read

    # TODO: deprecate in favour of fileResource.read_file
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
                    chunk = cast(bytes, self.byte_stream.read1())  # type: ignore
                    buffer += chunk
                    if not chunk:
                        break
                return buffer
            return self.byte_stream.read1(size)  # type: ignore

    # TODO: deprecate in favour of textResource.read_text
    def read_text(self, *, size: Optional[int] = None) -> str:
        """Read text into memory

        Returns:
            str: resource text
        """
        if self.memory:
            return ""
        with helpers.ensure_open(self):
            return self.text_stream.read(size)  # type: ignore

    # TODO: deprecate in favour of jsonResource.read_json
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
            helpers.pass_through(self.byte_stream)
            self.hash = f"sha256:{self.stats.sha256}"
            self.bytes = self.stats.bytes

    # Dereference

    def dereference(self):
        """Dereference underlaying metadata

        If some of underlaying metadata is provided as a string
        it will replace it by the metadata object
        """
        self.dialect.metadata_descriptor_path = None
        self.dialect.metadata_descriptor_initial = None
        self.schema.metadata_descriptor_path = None
        self.schema.metadata_descriptor_initial = None

    # Describe

    @classmethod
    def describe(
        cls,
        source: Optional[Any] = None,
        *,
        name: Optional[str] = None,
        type: Optional[str] = None,
        stats: bool = False,
        **options: Any,
    ) -> Metadata:
        """Describe the given source as a resource

        Parameters:
            source: data source
            name: resoucrce name
            type: data type: "package", "resource", "dialect", or "schema"
            stats: if `True` infer resource's stats
            **options: Resource constructor options

        Returns:
            Metadata: metadata describing this data source

        """
        Package = platform.frictionless.Package
        PackageResource = platform.frictionless_resources.PackageResource

        # Create resource
        resource = Resource(
            source,
            name=name or "",
            packagify=type == "package",
            **options,
        )

        # Package (guessed)
        if type in ["package", None] and isinstance(resource, PackageResource):
            package = resource.read_metadata()
            package.infer(stats=stats)
            if name is not None:
                return package.get_resource(name)
            return package

        # Package
        resource.infer(stats=stats)
        if type == "package":
            package = Package(resources=[resource])
            package.infer(stats=stats)
            if name is not None:
                return package.get_resource(name)
            return package

        # Dialect
        if type == "dialect":
            return resource.dialect

        # Schema
        if type == "schema":
            return resource.schema

        return resource

    # List

    def list(self, *, name: Optional[str] = None) -> List[Resource]:
        """List dataset resources

        Parameters:
            name: limit to one resource (if applicable)

        """
        return [self]

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
    ) -> Report:
        """Validate resource

        Parameters:
            checklist: a Checklist object
            name: limit validation to one resource (if applicable)
            on_row: callbacke for every row
            paraller: allow parallel validation (multiprocessing)
            limit_rows: limit amount of rows to this number
            limit_errors: limit amount of errors to this number

        Returns:
            Report: validation report

        """
        validator = Validator()
        return validator.validate_resource(self, checklist=checklist)

    # Export

    def to_copy(self, **options: Any) -> Self:
        """Create a copy from the resource"""
        return super().to_copy(
            data=self.data,
            basepath=self.basepath,
            detector=self.detector,
            package=self.package,
            **options,
        )

    # Metadata

    metadata_type = "resource"
    metadata_Error = errors.ResourceError
    metadata_profile = {
        "type": "object",
        "required": ["name"],  # TODO: add "type" in v6
        "properties": {
            "name": {"type": "string", "pattern": settings.NAME_PATTERN},
            "type": {"type": "string", "pattern": settings.TYPE_PATTERN},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "homepage": {"type": "string"},
            "profile": {"type": "string"},
            "licenses": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "path": {"type": "string"},
                        "title": {"type": "string"},
                    },
                },
            },
            "sources": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "path": {"type": "string"},
                        "email": {"type": "string"},
                    },
                },
            },
            "path": {"type": "string"},
            "data": {"type": ["object", "array"]},
            "scheme": {"type": "string"},
            "format": {"type": "string"},
            "mediatype": {"type": "string"},
            "compression": {"type": "string"},
            "extrapaths": {"type": "array", "item": {"type": "string"}},
            "innerpath": {"type": "string"},
            "encoding": {"type": "string"},
            "hash": {"type": "string"},
            "bytes": {"type": "integer"},
            "fields": {"type": "integer"},
            "rows": {"type": "integer"},
            "dialect": {"type": ["object", "string"]},
            "schema": {"type": ["object", "string"]},
        },
    }

    @classmethod
    def metadata_select_class(cls, type: Optional[str]):
        return system.select_resource_class(type)

    @classmethod
    def metadata_select_property_class(cls, name: str):
        if name == "dialect":
            return Dialect
        elif name == "schema":
            return Schema

    @classmethod
    def metadata_transform(cls, descriptor: types.IDescriptor):
        super().metadata_transform(descriptor)

        # Url (standards/v0)
        url = descriptor.pop("url", None)
        path = descriptor.get("path")
        data = descriptor.get("data")
        if not path and (data is None) and url:
            descriptor.setdefault("path", url)

        # Path (standards/v1)
        path = descriptor.get("path")
        if path and isinstance(path, list):
            descriptor["path"] = path[0]
            descriptor["extrapaths"] = path[1:]

        # Profiles (framework/v5)
        profiles = descriptor.pop("profiles", None)
        if isinstance(profiles, list) and profiles:
            if isinstance(profiles[0], str):
                descriptor["profile"] = profiles[0]

        # Bytes (standards/v1)
        bytes = descriptor.pop("bytes", None)
        if bytes:
            descriptor.setdefault("stats", {})
            descriptor["stats"]["bytes"] = bytes

        # Hash (framework/v4)
        hashing = descriptor.get("hashing", None)
        stats = descriptor.get("stats", None)
        if hashing and stats:
            hash = stats.pop("hash", None)
            if hash:
                descriptor[hashing] = hash
            note = 'Resource "stats.hash" is deprecated in favor of "stats.sha256/md5"'
            note += "(it will be removed in the next major version)"
            warnings.warn(note, UserWarning)

        # Hash (standards/v1)
        hash = descriptor.get("hash", None)
        if hash:
            algo, hash = helpers.parse_resource_hash_v1(hash)
            if algo in ["md5", "sha256"]:
                descriptor.pop("hash")
                descriptor.setdefault("stats", {})
                descriptor["stats"][algo] = hash

        # Stats (framework/v5)
        stats = descriptor.pop("stats", None)
        if stats and isinstance(stats, dict):
            md5 = stats.pop("md5", None)  # type: ignore
            sha256 = stats.pop("sha256", None)  # type: ignore
            if sha256:
                descriptor["hash"] = f"sha256:{sha256}"
            elif md5:
                descriptor["hash"] = md5
            for name in ["bytes", "fields", "rows"]:
                value = stats.get(name)  # type: ignore
                if value:
                    descriptor[name] = value

        # Compression (framework/v4)
        compression = descriptor.get("compression")
        if compression == "no":
            descriptor.pop("compression")
            note = 'Resource "compression=no" is deprecated in favor not set value'
            note += "(it will be removed in the next major version)"
            warnings.warn(note, UserWarning)

        # Profile (standards/v1)
        profile = descriptor.get("profile", None)
        if profile:
            if profile == "tabular-data-resource":
                descriptor["type"] = "table"

        # Layout (framework/v4)
        layout = descriptor.pop("layout", None)
        if layout:
            descriptor.setdefault("dialect", {})
            descriptor["dialect"].update(layout)
            note = 'Resource "layout" is deprecated in favor of "dialect"'
            note += "(it will be removed in the next major version)"
            warnings.warn(note, UserWarning)

    @classmethod
    def metadata_validate(cls, descriptor: types.IDescriptor):  # type: ignore
        metadata_errors = list(super().metadata_validate(descriptor))
        if metadata_errors:
            yield from metadata_errors
            return

        # Security
        if not system.trusted:
            keys = ["path", "extrapaths", "profile", "dialect", "schema"]
            for key in keys:
                value = descriptor.get(key)
                items = value if isinstance(value, list) else [value]  # type: ignore
                for item in items:  # type: ignore
                    if item and isinstance(item, str) and not helpers.is_safe_path(item):
                        yield errors.ResourceError(note=f'path "{item}" is not safe')
                        return

        # Required
        path = descriptor.get("path")
        data = descriptor.get("data")
        if path is None and data is None:
            note = 'one of the properties "path" or "data" is required'
            yield errors.ResourceError(note=note)

        # Path/Data
        if path is not None and data is not None:
            note = 'properties "path" and "data" is mutually exclusive'
            yield errors.ResourceError(note=note)

        # Licenses
        for item in descriptor.get("licenses", []):
            if not item.get("path") and not item.get("name"):
                note = f'license requires "path" or "name": {item}'
                yield errors.ResourceError(note=note)

        # Contributors/Sources
        for name in ["contributors", "sources"]:
            for item in descriptor.get(name, []):
                if item.get("email"):
                    field = fields.StringField(name="email", format="email")
                    _, note = field.read_cell(item.get("email"))
                    if note:
                        note = f'property "{name}[].email" is not valid "email"'
                        yield errors.ResourceError(note=note)

        # Profile
        profile = descriptor.get("profile")
        if profile and profile not in ["data-resource", "tabular-data-resource"]:
            yield from Metadata.metadata_validate(
                descriptor,
                profile=profile,
                error_class=cls.metadata_Error,
            )

        # Profile (tabular)
        schema = descriptor.get("schema")
        if profile == "tabular-data-resource":
            if not schema:
                note = 'profile "tabular-data-resource" requries "schema" to be present'
                yield errors.ResourceError(note=note)

        # Misleading
        for name in ["missingValues"]:
            if name in descriptor:
                note = f'"{name}" should be set as "schema.{name}"'
                yield errors.ResourceError(note=note)

    @classmethod
    def metadata_import(cls, descriptor: types.IDescriptor, **options: Any):
        return super().metadata_import(
            descriptor=descriptor,
            with_basepath=True,
            **options,
        )

    def metadata_export(self):  # type: ignore
        descriptor = super().metadata_export()

        # Data
        data = descriptor.get("data")
        types = (str, bool, int, float, list, dict)  # type: ignore
        if data is not None and not isinstance(data, types):
            descriptor["data"] = []

        # Path (standards/v1)
        if system.standards == "v1":
            path = descriptor.get("path")
            extrapaths = descriptor.pop("extrapaths", None)
            if extrapaths:
                descriptor["path"] = []
                if path:
                    descriptor["path"].append(path)  # type: ignore
                descriptor["path"].extend(extrapaths)  # type: ignore

        # Stats (standards/v1)
        if system.standards == "v1":
            stats = descriptor.pop("stats", None)
            if stats:
                sha256 = stats.get("sha256")
                md5 = stats.get("md5")
                bytes = stats.get("bytes")
                if sha256 is not None:
                    descriptor["hash"] = f"sha256:{sha256}"
                if md5 is not None:
                    descriptor["hash"] = md5
                if bytes is not None:
                    descriptor["bytes"] = bytes

        return descriptor
