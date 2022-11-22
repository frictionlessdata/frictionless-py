from typing import Optional, Any
from ...system import Adapter
from ...package import Package
from ...resource import Resource
from ...platform import platform
from ...helpers import slugify
from .control import ExcelControl


# TODO: implement properly
# TODO: move here book-related logic from parser (adapter wraps and keeps a book state)
# TODO: after the changes it should look more like SqlAdapter


class ExcelAdapter(Adapter):
    def __init__(self, control: ExcelControl, *, resource: Resource):
        self.control = control
        self.resource = resource

    # Read

    # TODO: dedup names
    def read_package(self) -> Package:
        package = Package(resources=[])
        with self.resource:
            book = platform.openpyxl.load_workbook(self.resource.byte_stream)
            for name in book.sheetnames:
                resource = Resource(
                    name=slugify(name),
                    path=self.resource.normpath,
                    control=ExcelControl(sheet=name),
                )
                package.add_resource(resource)
        return package

    # Write

    # TODO: implement
    def write_package(self, package: Package) -> Optional[Any]:
        pass
