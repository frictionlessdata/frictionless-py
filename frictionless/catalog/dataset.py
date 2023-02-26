from __future__ import annotations
import attrs
from typing import TYPE_CHECKING, Optional, ClassVar, Union
from ..metadata import Metadata
from ..package import Package
from .. import settings
from .. import errors

if TYPE_CHECKING:
    from .catalog import Catalog
    from ..interfaces import IDescriptor


@attrs.define(kw_only=True)
class Dataset(Metadata):
    """Dataset representation."""

    name: str
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “.”, “_” or “-” characters.
    """

    type: ClassVar[str]
    """
    A short name(preferably human-readable) for the Check.
    This MUST be lower-case and contain only alphanumeric characters
    along with "-" or "_".
    """

    title: Optional[str] = None
    """
    A human-readable title for the Check.
    """

    description: Optional[str] = None
    """
    A detailed description for the Check.
    """

    _package: Union[Package, str] = attrs.field(alias="package")
    """
    # TODO: add docs
    """

    _basepath: Optional[str] = attrs.field(default=None, alias="basepath")
    """
    # TODO: add docs
    """

    catalog: Optional[Catalog] = None
    """
    # TODO: add docs
    """

    def __attrs_post_init__(self):
        self._package_path: Optional[str] = None
        self._package_initial: Optional[IDescriptor] = None

    @property
    def package(self) -> Package:
        if isinstance(self._package, str):
            self._package_path = self._package
            self._package = Package.from_descriptor(self._package, basepath=self.basepath)
            self._package_initial = self._package.to_descriptor()
        return self._package

    @package.setter
    def package(self, value: Union[Package, str]):
        self._package = value

    @property
    def basepath(self) -> Optional[str]:
        if self._basepath:
            return self._basepath
        if self.catalog:
            return self.catalog.basepath

    @basepath.setter
    def basepath(self, value: Optional[str]):
        self._basepath = value

    # Metadata

    metadata_type = "dataset"
    metadata_Error = errors.DatasetError
    metadata_profile = {
        "type": "object",
        "required": ["name", "package"],
        "properties": {
            "name": {"type": "string", "pattern": settings.NAME_PATTERN},
            "type": {"type": "string", "pattern": settings.TYPE_PATTERN},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "package": {"type": ["object", "string"]},
        },
    }

    @classmethod
    def metadata_select_property_class(cls, name):
        if name == "package":
            return Package

    def metadata_export(self):
        descriptor = super().metadata_export()

        # Package
        package = descriptor.get("package")
        if self._package_path and self._package_initial == package:
            descriptor["package"] = self._package_path

        return descriptor
