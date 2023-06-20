from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional, Union

import attrs
from typing_extensions import Self

from .. import errors, fields, helpers, settings
from ..exception import FrictionlessException
from ..metadata import Metadata
from ..platform import platform
from ..resource import Resource
from ..system import system
from ..transformer import Transformer
from ..validator import Validator
from .factory import Factory

if TYPE_CHECKING:
    from .. import types
    from ..catalog import Dataset
    from ..checklist import Checklist
    from ..detector import Detector
    from ..dialect import Control, Dialect
    from ..indexer import IOnProgress, IOnRow
    from ..pipeline import Pipeline
    from ..resources import TableResource


@attrs.define(kw_only=True, repr=False)
class Package(Metadata, metaclass=Factory):
    """Package representation

    This class is one of the cornerstones of of Frictionless framework.
    It manages underlaying resource and provides an ability to describe a package.

    ```python
    package = Package(resources=[Resource(path="data/table.csv")])
    package.get_resoure('table').read_rows() == [
        {'id': 1, 'name': 'english'},
        {'id': 2, 'name': '中国人'},

    """

    source: Optional[Any] = attrs.field(default=None, kw_only=False)
    """
    # TODO: add docs
    """

    control: Optional[Control] = None
    """
    # TODO: add docs
    """

    _basepath: Optional[str] = attrs.field(default=None, alias="basepath")
    """
    # TODO: add docs
    """

    name: Optional[str] = None
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “.”, “_” or “-” characters.
    """

    type: ClassVar[Union[str, None]] = None
    """
    Type of the package
    """

    title: Optional[str] = None
    """
    A Package title according to the specs
    It should a human-oriented title of the resource.
    """

    description: Optional[str] = None
    """
    A Package description according to the specs
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
    The license(s) under which the package is provided.
    """

    sources: List[Dict[str, Any]] = attrs.field(factory=list)
    """
    The raw sources for this data package.
    It MUST be an array of Source objects.
    Each Source object MUST have a title and
    MAY have path and/or email properties.
    """

    contributors: List[Dict[str, Any]] = attrs.field(factory=list)
    """
    The people or organizations who contributed to this package.
    It MUST be an array. Each entry is a Contributor and MUST be an object.
    A Contributor MUST have a title property and MAY contain
    path, email, role and organization properties.
    """

    keywords: List[str] = attrs.field(factory=list)
    """
    An Array of string keywords to assist users searching.
    For example, ['data', 'fiscal']
    """

    image: Optional[str] = None
    """
    An image to use for this data package.
    For example, when showing the package in a listing.
    """

    version: Optional[str] = None
    """
    A version string identifying the version of the package.
    It should conform to the Semantic Versioning requirements and
    should follow the Data Package Version pattern.
    """

    created: Optional[str] = None
    """
    The datetime on which this was created.
    The datetime must conform to the string formats for RFC3339 datetime,
    """

    resources: List[Resource] = attrs.field(factory=list)
    """
    A list of resource descriptors.
    It can be dicts or Resource instances
    """

    dataset: Optional[Dataset] = None
    """
    It returns reference to dataset of which catalog the package is part of. If package
    is not part of any catalog, then it is set to None.
    """

    _dialect: Optional[Dialect] = attrs.field(default=None, alias="dialect")
    """
    # TODO: add docs
    """

    _detector: Optional[Detector] = attrs.field(default=None, alias="detector")
    """
    # TODO: add docs
    """

    def __attrs_post_init__(self):
        for resource in self.resources:
            resource.package = self
            if self._dialect:
                resource.dialect = self._dialect
            if self._detector:
                resource.detector = self._detector
        super().__attrs_post_init__()

    @property
    def basepath(self) -> Optional[str]:
        """
        A basepath of the package
        The normpath of the resource is joined `basepath` and `/path`
        """
        if self._basepath:
            return self._basepath
        if self.dataset:
            return self.dataset.basepath

    @basepath.setter
    def basepath(self, value: Optional[str]):
        self._basepath = value

    # Resources

    @property
    def resource_names(self) -> List[str]:
        """Return names of resources"""
        return [resource.name for resource in self.resources if resource.name is not None]  # type: ignore

    @property
    def resource_paths(self) -> List[str]:
        """Return names of resources"""
        return [resource.path for resource in self.resources if resource.path is not None]

    def add_resource(self, resource: Union[Resource, str]) -> Resource:
        """Add new resource to the package"""
        if isinstance(resource, str):
            resource = Resource.from_descriptor(resource, basepath=self.basepath)
        self.resources.append(resource)
        resource.package = self
        return resource

    def has_resource(self, name: str) -> bool:
        """Check if a resource is present"""
        for resource in self.resources:
            if resource.name == name:
                return True
        return False

    def has_table_resource(self, name: str) -> bool:
        """Check if a table resource is present"""
        for resource in self.resources:
            if resource.name == name:
                if isinstance(resource, platform.frictionless_resources.TableResource):
                    return True
        return False

    def get_resource(self, name: str) -> Resource:
        """Get resource by name"""
        for resource in self.resources:
            if resource.name == name:
                return resource
        error = errors.PackageError(note=f'resource "{name}" does not exist')
        raise FrictionlessException(error)

    def get_table_resource(self, name: str) -> TableResource:
        """Get table resource by name (raise if not table)"""
        resource = self.get_resource(name)
        if isinstance(resource, platform.frictionless_resources.TableResource):
            return resource
        error = errors.PackageError(note=f'resource "{name}" is not tabular')
        raise FrictionlessException(error)

    def set_resource(self, resource: Resource) -> Optional[Resource]:
        """Set resource by name"""
        assert resource.name
        if self.has_resource(resource.name):
            prev_resource = self.get_resource(resource.name)
            index = self.resources.index(prev_resource)
            self.resources[index] = resource
            resource.package = self
            return prev_resource
        self.add_resource(resource)

    def update_resource(self, name: str, descriptor: types.IDescriptor) -> Resource:
        """Update resource"""
        prev_resource = self.get_resource(name)
        resource_index = self.resources.index(prev_resource)
        resource_descriptor = prev_resource.to_descriptor()
        resource_descriptor.update(descriptor)
        new_resource = Resource.from_descriptor(resource_descriptor)
        new_resource.package = self
        self.resources[resource_index] = new_resource
        return prev_resource

    def remove_resource(self, name: str) -> Resource:
        """Remove resource by name"""
        resource = self.get_resource(name)
        self.resources.remove(resource)
        return resource

    def clear_resources(self):
        """Remove all the resources"""
        self.resources = []

    def deduplicate_resoures(self):
        if len(self.resource_names) != len(set(self.resource_names)):
            seen_names: List[str] = []
            for index, resource in enumerate(self.resources):
                name = resource.name
                count = seen_names.count(name) + 1
                if count > 1:
                    self.resources[index].name = "%s%s" % (name, count)
                seen_names.append(name)

    # Infer

    # TODO: allow cherry-picking stats for adding to a descriptor
    def infer(self, *, stats: bool = False) -> None:
        """Infer metadata

        Parameters:
            stats: stream files completely and infer stats
        """
        for resource in self.resources:
            resource.infer(stats=stats)

    # Publish

    def publish(self, target: Any = None, *, control: Optional[Control] = None) -> str:
        """Publish package to any supported data portal

        Parameters:
            target (string): url e.g. "https://github.com/frictionlessdata/repository-demo" of target[CKAN/Github...]
            control (dict): Github control

        Returns:
            Any: Response from the target
        """
        adapter = system.create_adapter(target, control=control, packagify=True)
        if not adapter:
            raise FrictionlessException(f"Not supported target: {target} or control")
        path = adapter.write_package(self.to_copy())
        if not path:
            raise FrictionlessException("Not supported action")
        return path

    # Flatten

    def flatten(self, spec: List[str] = ["name", "path"]):
        """Flatten the package

        Parameters
            spec (str[]): flatten specification

        Returns:
            any[]: flatten package
        """
        result: List[List[Any]] = []
        for resource in self.resources:
            context: Dict[str, Any] = {}
            context.update(resource.to_descriptor())
            result.append([context.get(prop) for prop in spec])
        return result

    # Dereference

    def dereference(self):
        """Dereference underlaying metadata

        If some of underlaying metadata is provided as a string
        it will replace it by the metadata object
        """
        for resource in self.resources:
            resource.dereference()

    # Analyze

    def analyze(self, *, detailed: bool = False):
        """Analyze the resources of the package

        This feature is currently experimental, and its API may change
        without warning.

        Parameters:
            detailed? (bool): detailed analysis

        Returns:
            dict: dict of resource analysis

        """
        analisis: Dict[str, Any] = {}
        for resource in self.resources:
            if isinstance(resource, platform.frictionless_resources.TableResource):
                analisis[resource.name] = resource.analyze(detailed=detailed)
        return analisis

    # Describe

    @classmethod
    def describe(
        cls,
        source: Optional[Any] = None,
        *,
        stats: bool = False,
        **options: Any,
    ):
        """Describe the given source as a package

        Parameters:
            source (any): data source
            stats? (bool): if `True` infer resource's stats
            **options (dict): Package constructor options

        Returns:
            Package: data package

        """
        metadata = Resource.describe(source, type="package", stats=stats, **options)
        assert isinstance(metadata, Package)
        return metadata

    # Extract

    def extract(
        self,
        *,
        name: Optional[str] = None,
        filter: Optional[types.IFilterFunction] = None,
        process: Optional[types.IProcessFunction] = None,
        limit_rows: Optional[int] = None,
    ) -> types.ITabularData:
        """Extract rows

        Parameters:
            filter: row filter function
            process: row processor function
            limit_rows: limit amount of rows to this number

        Returns:
            extracted rows indexed by resource name

        """
        data: types.ITabularData = {}
        resources = self.resources if name is None else [self.get_resource(name)]
        for res in resources:
            if isinstance(res, platform.frictionless_resources.TableResource):
                item = res.extract(filter=filter, process=process, limit_rows=limit_rows)
                data.update(item)
        return data

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
        names: List[str] = []
        resources = self.resources if name is None else [self.get_resource(name)]
        for resource in resources:
            if isinstance(resource, platform.frictionless_resources.TableResource):
                names.extend(
                    resource.index(
                        database_url=database_url,
                        fast=fast,
                        on_row=on_row,
                        on_progress=on_progress,
                        use_fallback=use_fallback,
                        qsv_path=qsv_path,
                    )
                )
        return names

    # Transform

    def transform(self: Package, pipeline: Pipeline):
        """Transform package

        Parameters:
            source (any): data source
            steps (Step[]): transform steps
            **options (dict): Package constructor options

        Returns:
            Package: the transform result
        """
        transformer = Transformer()
        return transformer.transform_package(self, pipeline)

    # Validate

    def validate(
        self: Package,
        checklist: Optional[Checklist] = None,
        *,
        name: Optional[str] = None,
        parallel: bool = False,
        limit_rows: Optional[int] = None,
        limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    ):
        """Validate package

        Parameters:
            checklist? (checklist): a Checklist object
            parallel? (bool): run in parallel if possible

        Returns:
            Report: validation report

        """
        validator = Validator()
        return validator.validate_package(
            self,
            checklist=checklist,
            name=name,
            parallel=parallel,
            limit_rows=limit_rows,
            limit_errors=limit_errors,
        )

    # Convert

    def to_copy(self, **options: Any) -> Self:
        """Create a copy of the package"""
        return super().to_copy(
            resources=[resource.to_copy() for resource in self.resources],
            basepath=self.basepath,
            dataset=self.dataset,
            **options,
        )

    def to_er_diagram(self, path: Optional[str] = None) -> str:
        """Generate ERD(Entity Relationship Diagram) from package resources
        and exports it as .dot file

        Based on:
        - https://github.com/frictionlessdata/frictionless-py/issues/1118

        Parameters:
            path (str): target path

        Returns:
            path(str): location of the .dot file
        """
        mapper = platform.frictionless_formats.erd.ErdMapper()
        text = mapper.write_package(self)
        if path:
            try:
                helpers.write_file(path, text)
            except Exception as exc:
                raise FrictionlessException(errors.PackageError(note=str(exc))) from exc
        return text

    # Metadata

    metadata_type = "package"
    metadata_Error = errors.PackageError
    metadata_profile = {
        "type": "object",
        "required": ["resources"],
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
            "contributors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "path": {"type": "string"},
                        "email": {"type": "string"},
                        "organisation": {"type": "string"},
                        "role": {"type": "string"},
                    },
                },
            },
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
            },
            "image": {"type": "string"},
            "version": {"type": "string"},
            "created": {"type": "string"},
            "resources": {
                "type": "array",
                "items": {"type": "object"},
            },
        },
    }

    @classmethod
    def metadata_select_class(cls, type: Optional[str]):
        return system.select_package_class(type)

    @classmethod
    def metadata_select_property_class(cls, name: str):
        if name == "resources":
            return Resource

    @classmethod
    def metadata_transform(cls, descriptor: types.IDescriptor):
        super().metadata_transform(descriptor)

        # Context
        descriptor.pop("$frictionless", None)

        # Profiles (framework/v5)
        profiles = descriptor.pop("profiles", None)
        if isinstance(profiles, list) and profiles:
            if isinstance(profiles[0], str):
                descriptor["profile"] = profiles[0]

    @classmethod
    def metadata_validate(cls, descriptor: types.IDescriptor):  # type: ignore
        metadata_errors = list(super().metadata_validate(descriptor))
        if metadata_errors:
            yield from metadata_errors
            return

        # Security
        if not system.trusted:
            keys = ["profile"]
            for key in keys:
                value = descriptor.get(key)
                items = value if isinstance(value, list) else [value]  # type: ignore
                for item in items:  # type: ignore
                    if item and isinstance(item, str) and not helpers.is_safe_path(item):
                        yield errors.PackageError(note=f'path "{item}" is not safe')
                        return

        # Resoruce Names
        resource_names: List[str] = []
        for resource in descriptor["resources"]:
            if isinstance(resource, dict) and "name" in resource:
                resource_names.append(resource["name"])  # type: ignore
        if len(resource_names) != len(set(resource_names)):
            note = "names of the resources are not unique"
            yield errors.PackageError(note=note)

        # Created
        created = descriptor.get("created")
        if created:
            field = fields.DatetimeField(name="created")
            _, note = field.read_cell(created)
            if note:
                note = 'property "created" is not valid "datetime"'
                yield errors.PackageError(note=note)

        # Licenses
        for item in descriptor.get("licenses", []):
            if not item.get("path") and not item.get("name"):
                note = f'license requires "path" or "name": {item}'
                yield errors.PackageError(note=note)

        # Contributors/Sources
        for name in ["contributors", "sources"]:
            for item in descriptor.get(name, []):
                if item.get("email"):
                    field = fields.StringField(name="email", format="email")
                    _, note = field.read_cell(item.get("email"))
                    if note:
                        note = f'property "{name}[].email" is not valid "email"'
                        yield errors.PackageError(note=note)

        # Profile
        profile = descriptor.get("profile")
        if profile and profile not in ["data-package", "tabular-data-package"]:
            if profile == "fiscal-data-package":
                profile = (
                    "https://specs.frictionlessdata.io/schemas/fiscal-data-package.json"
                )
            yield from Metadata.metadata_validate(
                descriptor,
                profile=profile,
                error_class=cls.metadata_Error,
            )

        # Profile (tabular)
        resources = descriptor.get("resources", [])
        if profile == "tabular-data-package":
            for resource in resources:
                if resource.get("profile", None) != "tabular-data-resource":
                    note = 'profile "tabular-data-package" requries all the resources to be "tabular-data-resource"'
                    yield errors.PackageError(note=note)

        # Misleading
        for name in ["missingValues", "fields"]:
            if name in descriptor:
                note = f'"{name}" should be set as "resource.schema.{name}"'
                yield errors.PackageError(note=note)

    @classmethod
    def metadata_import(cls, descriptor: types.IDescriptor, **options: Any):
        return super().metadata_import(
            descriptor=descriptor,
            with_basepath=True,
            **options,
        )

    def metadata_export(self):  # type: ignore
        descriptor = super().metadata_export()

        # TODO: recover after standards v2 release?
        # Frictionless
        #  if system.standards == "v2":
        #  descriptor = {"$frictionless": "package/v2", **descriptor}

        return descriptor
