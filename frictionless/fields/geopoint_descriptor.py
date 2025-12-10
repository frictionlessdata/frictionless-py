import json
from decimal import Decimal
from typing import Any, Literal, NamedTuple, Optional

from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import BaseConstraints


class geopoint(NamedTuple):
    """Internal representation of a geographic point"""
    lon: Decimal
    lat: Decimal

    def __repr__(self):
        return str([float(self[0]), float(self[1])])


class GeoPointFieldDescriptor(BaseFieldDescriptor):
    """The field contains data describing a geographic point."""

    type: Literal["geopoint"] = "geopoint"
    format: Optional[Literal["default", "array", "object"]] = None
    constraints: Optional[BaseConstraints[str]] = None

    def read_value(self, cell: Any) -> Optional[geopoint]:
        # Parse
        if isinstance(cell, str):
            try:
                if self.format == "default" or self.format is None:
                    lon, lat = cell.split(",")
                    lon = lon.strip()
                    lat = lat.strip()
                elif self.format == "array":
                    lon, lat = json.loads(cell)
                elif self.format == "object":
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

    def write_value(self, cell: Any) -> Optional[str]:
        if cell is None:
            return None
        format_value = self.format or "default"
        if format_value == "array":
            return json.dumps(list(cell))
        elif format_value == "object":
            return json.dumps({"lon": cell.lon, "lat": cell.lat})
        return ",".join(map(str, cell))

