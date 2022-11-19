from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic, Optional, Any
from ..dialect import Control

if TYPE_CHECKING:
    from ..catalog import Catalog
    from ..package import Package

ControlType = TypeVar("ControlType", bound=Control)


class Adapter(Generic[ControlType]):
    def __init__(self, control: ControlType):
        self.control = control

    # State

    control: ControlType
    """
    Control used to initialize the properties of the class while
    reading/writing package or catalog.
    """

    # Read

    def read_catalog(self) -> Optional[Catalog]:
        pass

    def read_package(self) -> Optional[Package]:
        pass

    # Write

    def write_catalog(self, catalog: Catalog) -> Optional[Any]:
        pass

    def write_package(self, package: Package) -> Optional[Any]:
        pass
