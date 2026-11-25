from __future__ import annotations

import os

from ... import types
from ...platform import platform
from ...resources import TableResource
from ...schema import Field
from ...system import Parser
from .control import ShapefileControl


class ShapefileParser(Parser):
    """Shapefile parser implementation."""

    supported_types = [
        "boolean",
        "date",
        "datetime",
        "integer",
        "number",
        "string",
    ]

    # Read

    def read_cell_stream_create(self) -> types.ICellStream:
        control = ShapefileControl.from_dialect(self.resource.dialect)
        layer = control.layer
        if not layer and self.resource.innerpath:
            layer = os.path.splitext(os.path.basename(self.resource.innerpath))[0]
        gdf = platform.geopandas.read_file(self.resource.normpath, layer=layer)

        # Geometries are exposed as WKT strings
        names = list(gdf.columns[gdf.dtypes == "geometry"])
        df = platform.pandas.DataFrame(gdf.drop(columns=names))
        for name in names:
            wkt = gdf[name].to_wkt()
            df[name] = wkt.astype(object).where(wkt.notna(), None)
        df = df[list(gdf.columns)]

        with TableResource(data=df, format="pandas") as resource:
            schema = resource.schema
            for name in names:
                descriptor = {"name": name, "type": "string", "format": "wkt"}
                schema.set_field(Field.from_descriptor(descriptor))
            if not self.resource.schema:
                self.resource.schema = schema
            yield from resource.cell_stream
