from __future__ import annotations
import os
from pathlib import Path
from collections.abc import Mapping
from typing import TYPE_CHECKING, Optional, List, Any, Union
from ..exception import FrictionlessException
from ..platform import platform
from ..metadata import Metadata
from ..resource import Resource
from ..system import system
from .. import settings
from .. import helpers
from .. import errors
from .. import fields
from . import methods

if TYPE_CHECKING:
    from ..interfaces import IDescriptor, IProfile
    from ..dialect import Dialect, Control
    from ..detector import Detector
    from ..catalog import Catalog


# TODO: think about package/resource/schema/etc extension mechanism (e.g. FiscalPackage)
class Package(Metadata):
    """Package representation

    This class is one of the cornerstones of of Frictionless framework.
    It manages underlaying resource and provides an ability to describe a package.

    ```python
    package = Package(resources=[Resource(path="data/table.csv")])
    package.get_resoure('table').read_rows() == [
        {'id': 1, 'name': 'english'},
        {'id': 2, 'name': '中国人'},

    """

    analyze = methods.analyze
    describe = methods.describe
    extract = methods.extract
    transform = methods.transform
    validate = methods.validate

    def __init__(
        self,
        source: Optional[Any] = None,
        control: Optional[Control] = None,
        *,
        # Standard
        name: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        homepage: Optional[str] = None,
        profiles: List[Union[IProfile, str]] = [],
        licenses: List[dict] = [],
        sources: List[dict] = [],
        contributors: List[dict] = [],
        keywords: List[str] = [],
        image: Optional[str] = None,
        version: Optional[str] = None,
        created: Optional[str] = None,
        resources: List[Union[Resource, str]] = [],
        # Software
        basepath: Optional[str] = None,
        detector: Optional[Detector] = None,
        dialect: Optional[Dialect] = None,
        catalog: Optional[Catalog] = None,
    ):

        # Store state
        self.name = name
        self.title = title
        self.description = description
        self.profiles = profiles.copy()
        self.licenses = licenses.copy()
        self.sources = sources.copy()
        self.homepage = homepage
        self.contributors = contributors.copy()
        self.keywords = keywords.copy()
        self.image = image
        self.version = version
        self.created = created
        self.basepath = basepath
        self.catalog = catalog

        # Add resources
        self.resources = []
        for resource in resources:
            resource = self.add_resource(resource)
            if detector:
                resource.detector = detector
            if dialect:
                resource.dialect = dialect

        # Handled by the create hook
        assert source is None
        assert control is None

    # TODO: support list of paths as resource paths?
    @classmethod
    def __create__(
        cls,
        source: Optional[Any] = None,
        *,
        control: Optional[Control] = None,
        **options,
    ):
        if source is not None or control is not None:

            # Path
            if isinstance(source, Path):
                source = str(source)

            # Mapping
            elif isinstance(source, Mapping):
                source = {key: value for key, value in source.items()}

            # Directory
            elif helpers.is_directory_source(source):
                for name in ["datapackage.json", "datapackage.yaml"]:
                    path = os.path.join(source, name)  # type: ignore
                    if os.path.isfile(path):
                        return Package.from_descriptor(path)

            # Expandable
            elif helpers.is_expandable_source(source):
                options["resources"] = []
                basepath = options.get("basepath")
                for path in helpers.expand_source(source, basepath=basepath):  # type: ignore
                    options["resources"].append(Resource(path=path))
                return Package.from_options(**options)

            # Adapter
            adapter = system.create_adapter(source, control=control)
            if adapter:
                package = adapter.read_package()
                if package:
                    return package

            # Descriptor
            if helpers.is_descriptor_source(source):
                return Package.from_descriptor(source, **options)  # type: ignore

            # Path/data
            options["resources"] = [Resource(source)]
            return Package(**options)

    # State

    name: Optional[str]
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “.”, “_” or “-” characters.
    """

    title: Optional[str]
    """
    A Package title according to the specs
    It should a human-oriented title of the resource.
    """

    description: Optional[str]
    """
    A Package description according to the specs
    It should a human-oriented description of the resource.
    """

    homepage: Optional[str]
    """
    A URL for the home on the web that is related to this package.
    For example, github repository or ckan dataset address.
    """

    profiles: List[Union[IProfile, str]]
    """
    A strings identifying the profiles of this descriptor.
    For example, `fiscal-data-package`.
    """

    licenses: List[dict]
    """
    The license(s) under which the package is provided.
    """

    sources: List[dict]
    """
    The raw sources for this data package.
    It MUST be an array of Source objects.
    Each Source object MUST have a title and
    MAY have path and/or email properties.
    """

    contributors: List[dict]
    """
    The people or organizations who contributed to this package.
    It MUST be an array. Each entry is a Contributor and MUST be an object.
    A Contributor MUST have a title property and MAY contain
    path, email, role and organization properties.
    """

    keywords: List[str]
    """
    An Array of string keywords to assist users searching.
    For example, ['data', 'fiscal']
    """

    image: Optional[str]
    """
    An image to use for this data package.
    For example, when showing the package in a listing.
    """

    version: Optional[str]
    """
    A version string identifying the version of the package.
    It should conform to the Semantic Versioning requirements and
    should follow the Data Package Version pattern.
    """

    created: Optional[str]
    """
    The datetime on which this was created.
    The datetime must conform to the string formats for RFC3339 datetime,
    """

    resources: List[Resource]
    """
    A list of resource descriptors.
    It can be dicts or Resource instances
    """

    catalog: Optional[Catalog]
    """
    It returns reference to catalog of which the package is part of. If package
    is not part of any catalog, then it is set to None.
    """

    # Props

    @property
    def resource_names(self) -> List[str]:
        """Return names of resources"""
        return [resource.name for resource in self.resources if resource.name is not None]

    @property
    def resource_paths(self) -> List[str]:
        """Return names of resources"""
        return [resource.path for resource in self.resources if resource.path is not None]

    @property
    def basepath(self) -> Optional[str]:
        """
        A basepath of the package
        The normpath of the resource is joined `basepath` and `/path`
        """
        if self.__basepath:
            return self.__basepath
        if self.catalog:
            return self.catalog.basepath

    @basepath.setter
    def basepath(self, value: Optional[str]):
        self.__basepath = value

    # Resources

    def add_resource(self, resource: Union[Resource, str]) -> Resource:
        """Add new resource to the package"""
        if isinstance(resource, str):
            resource = Resource.from_descriptor(resource, basepath=self.basepath)
        if resource.name and self.has_resource(resource.name):
            error = errors.PackageError(note=f'resource "{resource.name}" already exists')
            raise FrictionlessException(error)
        self.resources.append(resource)
        resource.package = self
        return resource

    def has_resource(self, name: str) -> bool:
        """Check if a resource is present"""
        for resource in self.resources:
            if resource.name == name:
                return True
        return False

    def get_resource(self, name: str) -> Resource:
        """Get resource by name"""
        for resource in self.resources:
            if resource.name == name:
                return resource
        error = errors.PackageError(note=f'resource "{name}" does not exist')
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

    def update_resource(self, name: str, descriptor: IDescriptor) -> Resource:
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

    # Infer

    def infer(self, *, sample=True, stats=False):
        """Infer package's attributes

        Parameters:
            sample? (bool): open files and infer from a sample (default: True)
            stats? (bool): stream files completely and infer stats
        """

        # General
        for resource in self.resources:
            resource.infer(sample=sample, stats=stats)

        # Deduplicate names
        if len(self.resource_names) != len(set(self.resource_names)):
            seen_names = []
            for index, name in enumerate(self.resource_names):
                count = seen_names.count(name) + 1
                if count > 1:
                    self.resources[index].name = "%s%s" % (name, count)
                seen_names.append(name)

    # Publish

    def publish(self, target: Any = None, *, control: Optional[Control] = None) -> Any:
        """Publish package to any supported data portal

        Parameters:
            target (string): url e.g. "https://github.com/frictionlessdata/repository-demo" of target[CKAN/Github...]
            control (dict): Github control

        Returns:
            Any: Response from the target
        """
        adapter = system.create_adapter(target, control=control)
        if not adapter:
            raise FrictionlessException(f"Not supported target: {target} or control")
        response = adapter.write_package(self.to_copy())
        if not response:
            raise FrictionlessException("Not supported action")
        return response

    # Flatten

    def flatten(self, spec=["name", "path"]):
        """Flatten the package

        Parameters
            spec (str[]): flatten specification

        Returns:
            any[]: flatten package
        """
        result = []
        for resource in self.resources:
            context = {}
            context.update(resource.to_descriptor())
            result.append([context.get(prop) for prop in spec])
        return result

    # Convert

    def to_copy(self):
        """Create a copy of the package"""
        return super().to_copy(
            resources=[resource.to_copy() for resource in self.resources]
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
            "title": {"type": "string"},
            "description": {"type": "string"},
            "homepage": {"type": "string"},
            "profiles": {"type": "array"},
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
                "items": {"type": ["object", "string"]},
            },
        },
    }

    @classmethod
    def metadata_specify(cls, *, type=None, property=None):
        if property == "resources":
            return Resource

    @classmethod
    def metadata_transform(cls, descriptor: IDescriptor):
        super().metadata_transform(descriptor)

        # Profile (standards/v1)
        profile = descriptor.pop("profile", None)
        if profile:
            if profile not in ["data-package", "tabular-data-package"]:
                descriptor.setdefault("profiles", [])
                descriptor["profiles"].append(profile)

    @classmethod
    def metadata_validate(cls, descriptor: IDescriptor):
        metadata_errors = list(super().metadata_validate(descriptor))
        if metadata_errors:
            yield from metadata_errors
            return

        # Security
        if not system.trusted:
            keys = ["resources", "profiles"]
            for key in keys:
                value = descriptor.get(key)
                items = value if isinstance(value, list) else [value]
                for item in items:
                    if item and isinstance(item, str) and not helpers.is_safe_path(item):
                        yield errors.PackageError(note=f'path "{item}" is not safe')
                        return

        # Resoruce Names
        resource_names = []
        for resource in descriptor["resources"]:
            if isinstance(resource, dict) and "name" in resource:
                resource_names.append(resource["name"])
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
            if not item.get("path") or not item.get("name"):
                note = f'license requires "path" or "name": {item}'
                yield errors.PackageError(note=note)

        # Contributors/Sources
        for name in ["contributors", "sources"]:
            for item in descriptor.get(name, []):
                if item.get("email"):
                    field = fields.StringField(format="email")
                    _, note = field.read_cell(item.get("email"))
                    if note:
                        note = f'property "{name}[].email" is not valid "email"'
                        yield errors.PackageError(note=note)

        # Profiles
        profiles = descriptor.get("profiles", [])
        for profile in profiles:
            if profile in ["data-package", "tabular-data-package"]:
                continue
            yield from Metadata.metadata_validate(
                descriptor,
                profile=profile,
                error_class=cls.metadata_Error,
            )

        # Misleading
        for name in ["missingValues", "fields"]:
            if name in descriptor:
                note = f'"{name}" should be set as "resource.schema.{name}"'
                yield errors.PackageError(note=note)

    @classmethod
    def metadata_import(cls, descriptor: IDescriptor, **options):
        return super().metadata_import(
            descriptor=descriptor,
            with_basepath=True,
            **options,
        )

    def metadata_export(self):
        descriptor = super().metadata_export()

        # Profile (standards/v1)
        if system.standards == "v1":
            profiles = descriptor.pop("profiles", None)
            descriptor["profile"] = "data-package"
            if profiles:
                descriptor["profile"] = profiles[0]

        return descriptor
