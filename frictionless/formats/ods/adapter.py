import io

from ...helpers import slugify
from ...package import Package
from ...platform import platform
from ...resource import Resource
from ...system import Adapter
from .control import OdsControl

# TODO: implement properly
# TODO: move here book-related logic from parser (adapter wraps and keeps a book state)
# TODO: after the changes it should look more like SqlAdapter


class OdsAdapter(Adapter):
    def __init__(self, control: OdsControl, *, resource: Resource):
        self.control = control
        self.resource = resource

    # Read

    def read_package(self) -> Package:
        package = Package()
        with self.resource:
            bytes = io.BytesIO(self.resource.byte_stream.read())
            book = platform.ezodf.opendoc(bytes)
            for sheet in book.sheets:
                resource = Resource(
                    name=slugify(sheet.name),
                    path=self.resource.normpath,
                    control=OdsControl(sheet=sheet.name),
                )
                package.add_resource(resource)
        package.deduplicate_resoures()
        return package

    # Write

    # TODO: implement
    #  def write_package(self, package: Package):
    #  pass
