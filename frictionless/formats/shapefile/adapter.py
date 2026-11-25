from __future__ import annotations

from typing import Optional

from ... import helpers
from ...package import Package
from ...platform import platform
from ...resources import TableResource
from ...system import Adapter
from .control import ShapefileControl


class ShapefileAdapter(Adapter):
    """Read a zipped shapefile as a package with a resource per layer"""

    def __init__(
        self,
        source: str,
        *,
        control: Optional[ShapefileControl] = None,
        basepath: Optional[str] = None,
    ):
        self.source = source
        self.control = control or ShapefileControl()
        self.basepath = basepath

    # Read

    def read_package(self):
        package = Package(basepath=self.basepath)
        fullpath = helpers.join_basepath(self.source, basepath=self.basepath)
        for layer, _ in platform.pyogrio.list_layers(fullpath):
            if self.control.layer and layer != self.control.layer:
                continue
            resource = TableResource(
                name=helpers.slugify(layer, regex_pattern=r"[^-a-z0-9._/]"),
                path=self.source,
                format="shp",
                control=ShapefileControl(layer=layer),
            )
            package.add_resource(resource)
        return package
