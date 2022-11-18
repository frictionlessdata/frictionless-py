from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic
from ..dialect import Control

if TYPE_CHECKING:
    from .package import Package
    from ..catalog import Catalog

ControlType = TypeVar("ControlType", bound=Control)


# TODO: remove here and in the system after rebase to Adapter
class Manager(Generic[ControlType]):
    # TODO: shall we accept aslo source?
    def __init__(self, control: ControlType):
        self.control = control

    # State

    control: ControlType
    """
    Control used to initialize the properties of the class while
    reading/writing package or catalog.
    """

    # Read

    def read_catalog(self) -> Catalog:
        raise NotImplementedError()

    def read_package(self) -> Package:
        raise NotImplementedError()

    # Write

    def write_catalog(self, catalog: Catalog):
        raise NotImplementedError()

    def write_package(self, package: Package):
        raise NotImplementedError()
