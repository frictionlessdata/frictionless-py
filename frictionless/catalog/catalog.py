from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Any, Union
from ..exception import FrictionlessException
from ..metadata import Metadata
from ..package import Package
from ..system import system
from .. import settings
from .. import helpers
from .. import errors

if TYPE_CHECKING:
    from ..dialect import Control
    from ..interfaces import IDescriptor

# TODO: we need to support opening dir as a catalog using datacatalog.yaml


class Catalog(Metadata):
    """Catalog representation"""

    def __init__(
        self,
        source: Optional[Any] = None,
        *,
        control: Optional[Control] = None,
        # Standard
        name: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        packages: List[Union[Package, str]] = [],
        # Software
        basepath: Optional[str] = None,
    ):

        # Store state
        self.name = name
        self.title = title
        self.description = description
        self.basepath = basepath

        # Add packages
        self.packages = []
        for package in packages:
            package = self.add_package(package)

        # Handled by the create hook
        assert source is None
        assert control is None

    @classmethod
    def __create__(
        cls, source: Optional[Any] = None, *, control: Optional[Control] = None, **options
    ):
        if source is not None or control is not None:

            # Adapter
            adapter = system.create_adapter(source, control=control)
            if adapter:
                catalog = adapter.read_catalog()
                if catalog:
                    return catalog

            # Descriptor
            if helpers.is_descriptor_source(source):
                return Catalog.from_descriptor(source, **options)  # type: ignore

    # State

    name: Optional[str]
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “.”, “_” or “-” characters.
    """

    title: Optional[str]
    """
    A Catalog title according to the specs. It should be a
    human-oriented title of the resource.
    """

    description: Optional[str]
    """
    A Catalog description according to the specs. It should be a
    human-oriented description of the resource.
    """

    packages: List[Package]
    """
    A list of packages. Each package in the list is a Data Package.
    """

    basepath: Optional[str]
    """
    A basepath of the catalog. The normpath of the resource is joined
    `basepath` and `/path`
    """

    # Props

    @property
    def package_names(self) -> List[str]:
        """Return names of packages"""
        return [package.name for package in self.packages if package.name is not None]

    # Packages

    def add_package(self, package: Union[Package, str]) -> Package:
        """Add new package to the package"""
        if isinstance(package, str):
            package = Package.from_descriptor(package, basepath=self.basepath)
        if package.name and self.has_package(package.name):
            error = errors.PackageError(note=f'package "{package.name}" already exists')
            raise FrictionlessException(error)
        self.packages.append(package)
        package.catalog = self
        return package

    def has_package(self, name: str) -> bool:
        """Check if a package is present"""
        for package in self.packages:
            if package.name == name:
                return True
        return False

    def get_package(self, name: str) -> Package:
        """Get package by name"""
        for package in self.packages:
            if package.name == name:
                return package
        error = errors.CatalogError(note=f'package "{name}" does not exist')
        raise FrictionlessException(error)

    def set_package(self, package: Package) -> Optional[Package]:
        """Set package by name"""
        assert package.name
        if self.has_package(package.name):
            prev_package = self.get_package(package.name)
            index = self.packages.index(prev_package)
            self.packages[index] = package
            package.package = self
            return prev_package
        self.add_package(package)

    def remove_package(self, name: str) -> Package:
        """Remove package by name"""
        package = self.get_package(name)
        self.packages.remove(package)
        return package

    def clear_packages(self):
        """Remove all the packages"""
        self.packages = []

    # Infer

    def infer(self, *, sample=True, stats=False):
        """Infer catalog's metadata

        Parameters:
            sample? (bool): open files and infer from a sample (default: True)
            stats? (bool): stream files completely and infer stats
        """

        # General
        for number, package in enumerate(self.packages, start=1):
            package.infer(sample=sample, stats=stats)
            package.name = package.name or f"package{number}"

        # TODO: move to helpers and re-use
        # Deduplicate names
        if len(self.package_names) != len(set(self.package_names)):
            seen_names = []
            for index, name in enumerate(self.package_names):
                count = seen_names.count(name) + 1
                if count > 1:
                    self.packages[index].name = "%s%s" % (name, count)
                seen_names.append(name)

    # Metadata

    metadata_type = "catalog"
    metadata_Error = errors.CatalogError
    metadata_profile = {
        "type": "object",
        "required": ["packages"],
        "properties": {
            "name": {"type": "string", "pattern": settings.NAME_PATTERN},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "packages": {
                "type": "array",
                "items": {"type": ["object", "string"]},
            },
        },
    }

    @classmethod
    def metadata_specify(cls, *, type=None, property=None):
        if property == "packages":
            return Package

    @classmethod
    def metadata_import(cls, descriptor: IDescriptor, **options):
        return super().metadata_import(
            descriptor=descriptor,
            with_basepath=True,
            **options,
        )
