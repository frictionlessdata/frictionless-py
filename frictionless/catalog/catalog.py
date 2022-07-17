from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Any
from ..exception import FrictionlessException
from ..metadata import Metadata
from ..package import Package
from ..system import system
from .. import settings
from .. import errors

if TYPE_CHECKING:
    from ..dialect import Control


class Catalog(Metadata):
    """Catalog representation"""

    def __init__(
        self,
        source: Optional[Any] = None,
        *,
        # Standard
        name: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        packages: List[Package] = [],
        # Software
        control: Optional[Control] = None,
    ):

        # Store state
        self.name = name
        self.title = title
        self.description = description
        self.packages = packages.copy()

        # Handled by the create hook
        assert source is None
        assert control is None

    @classmethod
    def __create__(cls, source: Optional[Any] = None, **options):
        if source is not None:

            # Manager
            control = options.pop("control", None)
            manager = system.create_manager(source, control=control)
            if manager:
                catalog = manager.read_catalog()
                return catalog

    # State

    name: Optional[str]
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “.”, “_” or “-” characters.
    """

    title: Optional[str]
    """
    A Catalog title according to the specs
    It should a human-oriented title of the resource.
    """

    description: Optional[str]
    """
    A Catalog description according to the specs
    It should a human-oriented description of the resource.
    """

    # Props

    @property
    def package_names(self) -> List[str]:
        """Return names of packages"""
        return [package.name for package in self.packages if package.name is not None]

    # Packages

    def add_package(self, package: Package) -> None:
        """Add new package to the package"""
        if package.name and self.has_package(package.name):
            error = errors.PackageError(note=f'package "{package.name}" already exists')
            raise FrictionlessException(error)
        self.packages.append(package)
        package.package = self

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
    metadata_Types = dict(packages=Package)
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
