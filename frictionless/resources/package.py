from ..package import Package
from .json import JsonResource


class PackageResource(JsonResource):
    datatype = "package"

    def read_package(self) -> Package:
        assert self.normpath
        return Package.from_descriptor(self.normpath)
