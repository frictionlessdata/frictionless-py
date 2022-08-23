from __future__ import annotations
import json
import attrs
from collections import namedtuple
from decimal import Decimal
from ..schema import Field


@attrs.define(kw_only=True)
class GeopointField(Field):
    type = "geopoint"
    builtin = True
    supported_constraints = [
        "required",
        "enum",
    ]

    # Read

    def create_value_reader(self):

        # Create reader
        def value_reader(cell):

            # Parse
            if isinstance(cell, str):
                try:
                    if self.format == "default":
                        lon, lat = cell.split(",")
                        lon = lon.strip()
                        lat = lat.strip()
                    elif self.format == "array":
                        lon, lat = json.loads(cell)
                    elif self.format == "object":
                        if isinstance(cell, str):
                            cell = json.loads(cell)
                        if len(cell) != 2:
                            return None
                        lon = cell["lon"]
                        lat = cell["lat"]
                    cell = geopoint(Decimal(lon), Decimal(lat))  # type: ignore
                except Exception:
                    return None

            # Validate
            try:
                cell = geopoint(*cell)
                if cell.lon > 180 or cell.lon < -180:
                    return None
                if cell.lat > 90 or cell.lat < -90:
                    return None
            except Exception:
                return None

            return cell

        return value_reader

    # Write

    def create_value_writer(self):

        # Create writer
        def value_writer(cell):
            if self.format == "array":
                return json.dumps(list(cell))
            elif self.format == "object":
                return json.dumps({"lon": cell.lon, "lat": cell.lat})
            return ",".join(map(str, cell))

        return value_writer


# Internal

geopoint = namedtuple("geopoint", ["lon", "lat"])
geopoint.__repr__ = lambda self: str([float(self[0]), float(self[1])])  # type: ignore
