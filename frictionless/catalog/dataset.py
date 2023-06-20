from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Optional, Union

import attrs

from .. import errors, settings
from ..metadata import Metadata
from ..package import Package

if TYPE_CHECKING:
    from .catalog import Catalog


@attrs.define(kw_only=True, repr=False)
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

    @property
    def package(self) -> Package:
        if isinstance(self._package, str):
            self._package = Package.from_descriptor(self._package, basepath=self.basepath)
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

    # Infer

    def infer(self, *, stats: bool = False):
        """Infer dataset's metadata

        Parameters:
            stats? (bool): stream files completely and infer stats
        """
        self.package.infer(stats=stats)

    # Dereference

    def dereference(self):
        """Dereference underlaying metadata

        If some of underlaying metadata is provided as a string
        it will replace it by the metadata object
        """
        self.package.metadata_descriptor_path = None
        self.package.metadata_descriptor_initial = None

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
    def metadata_select_property_class(cls, name: str):
        if name == "package":
            return Package
