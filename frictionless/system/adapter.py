from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ..catalog import Catalog
    from ..package import Package


# NOTE:
# There should be a way to check the supported functionality of a concrete adapter
# For example, does it suport `read_catalog`? We can implement it based on what
# methods return (or not) or use some kins of `supported_actions` property


class Adapter:
    # Read

    def read_catalog(self) -> Optional[Catalog]:
        pass

    def read_package(self) -> Optional[Package]:
        pass

    # Write

    def write_catalog(self, catalog: Catalog) -> Any:
        raise NotImplementedError()

    def write_package(self, package: Package) -> Any:
        raise NotImplementedError()
