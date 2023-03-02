from __future__ import annotations
from ..package import Package
from .json import JsonResource


class PackageResource(JsonResource):
    datatype = "package"

    def read_package(self) -> Package:
        descriptor = self.data if self.data is not None else self.path
        assert isinstance(descriptor, (str, dict))
        return Package.from_descriptor(descriptor, basepath=self.basepath)
