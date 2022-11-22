import io
from typing import Optional, Any
from ...system import Adapter
from ...package import Package
from ...resource import Resource
from ...platform import platform
from ...helpers import slugify
from .control import OdsControl


# TODO: implement properly
# TODO: move here book-related logic from parser (adapter wraps and keeps a book state)
# TODO: after the changes it should look more like SqlAdapter


class OdsAdapter(Adapter):
    def __init__(self, control: OdsControl, *, resource: Resource):
        self.control = control
        self.resource = resource

    # Read

    # TODO: dedup names
    def read_package(self) -> Package:
        package = Package(resources=[])
        with self.resource:
            book = platform.ezodf.opendoc(io.BytesIO(self.resource.byte_stream.read()))
            for sheet in book.sheets:
                resource = Resource(
                    name=slugify(sheet.name),
                    path=self.resource.normpath,
                    control=OdsControl(sheet=sheet.name),
                )
                package.add_resource(resource)
        return package

    # Write

    # TODO: implement
    def write_package(self, package: Package) -> Optional[Any]:
        pass
