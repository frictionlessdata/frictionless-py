from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Optional

from ... import helpers
from ...platform import platform
from ...system import Plugin
from .adapter import ShapefileAdapter
from .control import ShapefileControl
from .parser import ShapefileParser

if TYPE_CHECKING:
    from ...dialect import Control
    from ...resource import Resource


class ShapefilePlugin(Plugin):
    """Plugin for ESRI Shapefile"""

    # Hooks

    def create_adapter(
        self,
        source: Any,
        *,
        control: Optional[Control] = None,
        basepath: Optional[str] = None,
        packagify: bool = False,
    ):
        if not isinstance(source, str):
            return
        fullpath = helpers.join_basepath(source, basepath=basepath)
        _, format = helpers.parse_scheme_and_format(fullpath)
        if format != "zip" or not is_zipped_shapefile(fullpath):
            return
        control = control if isinstance(control, ShapefileControl) else None
        # A single layer is a table resource unless a package is requested
        if not packagify:
            if control and control.layer:
                return
            if len(platform.pyogrio.list_layers(fullpath)) < 2:
                return
        return ShapefileAdapter(source, control=control, basepath=basepath)

    def create_parser(self, resource: Resource):
        if resource.format == "shp":
            return ShapefileParser(resource)

    def detect_resource(self, resource: Resource):
        # A zipped shapefile is read as a whole by GDAL, not decompressed
        if resource.compression == "zip" and resource.format in [None, "", "shp"]:
            if resource.format == "shp" or is_zipped_shapefile(resource.normpath):
                resource.format = "shp"
                resource.compression = None
        if resource.format == "shp":
            resource.datatype = resource.datatype or "table"
            resource.mediatype = resource.mediatype or "application/vnd.shp"

    def select_control_class(self, type: Optional[str] = None):
        if type == "shapefile":
            return ShapefileControl


def is_zipped_shapefile(path: Optional[str]) -> bool:
    """Check if a local zip archive contains a shapefile but not a data package"""
    if not path or helpers.is_remote_path(path) or not os.path.isfile(path):
        return False
    try:
        with platform.zipfile.ZipFile(path, "r") as zip:
            names = zip.namelist()
    except platform.zipfile.BadZipFile:
        return False
    if "datapackage.json" in names:
        return False
    return any(name.lower().endswith(".shp") for name in names)
