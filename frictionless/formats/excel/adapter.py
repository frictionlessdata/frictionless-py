from typing import Any, Optional

from ...helpers import slugify
from ...package import Package
from ...platform import platform
from ...resource import Resource
from ...system import Adapter
from .control import ExcelControl

# TODO: implement properly
# TODO: move here book-related logic from parser (adapter wraps and keeps a book state)
# TODO: after the changes it should look more like SqlAdapter


class ExcelAdapter(Adapter):
    def __init__(self, control: ExcelControl, *, resource: Resource):
        self.control = control
        self.resource = resource

    # Read

    def read_package(self) -> Package:
        package = Package()
        with self.resource:
            book = platform.openpyxl.load_workbook(self.resource.byte_stream)
            for name in book.sheetnames:
                resource = Resource(
                    name=slugify(name),
                    path=self.resource.normpath,
                    control=ExcelControl(sheet=name),
                )
                package.add_resource(resource)
        package.deduplicate_resoures()
        return package

    # Write

    # TODO: implement
    def write_package(self, package: Package) -> Optional[Any]:
        pass
