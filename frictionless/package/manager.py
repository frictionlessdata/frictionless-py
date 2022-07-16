from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .package import Package
    from ..catalog import Catalog


class Manager:
    def __init__(self, source, **options):
        raise NotImplementedError()

    # Read

    def read_catalog(self, **options) -> Catalog:
        raise NotImplementedError()

    def read_package(self, **options) -> Package:
        raise NotImplementedError()

    # Write

    def write_catalog(self, catalog: Catalog, **options):
        raise NotImplementedError()

    def write_package(self, package: Package, **options):
        raise NotImplementedError()
