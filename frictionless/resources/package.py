from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from ..package import Package
from .json import JsonResource

if TYPE_CHECKING:
    from ..interfaces import IFilterFunction, IProcessFunction, IExtractedRows


class PackageResource(JsonResource):
    datatype = "package"

    def extract(
        self,
        *,
        name: Optional[str] = None,
        filter: Optional[IFilterFunction] = None,
        process: Optional[IProcessFunction] = None,
        limit_rows: Optional[int] = None,
    ) -> IExtractedRows:
        package = self.read_package()
        return package.extract(
            name=name, filter=filter, process=process, limit_rows=limit_rows
        )

    def read_package(self) -> Package:
        descriptor = self.data if self.data is not None else self.path
        assert isinstance(descriptor, (str, dict))
        return Package.from_descriptor(descriptor, basepath=self.basepath)
