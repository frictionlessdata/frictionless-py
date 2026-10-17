import json
from decimal import Decimal

import pytest

from frictionless import Field

# General


@pytest.mark.parametrize(
    "format, source, target",
    [
        ("default", (180, 90), (180, 90)),
        ("default", [180, 90], (180, 90)),
        ("default", "180,90", (180, 90)),
        ("default", "180, -90", (180, -90)),
        ("default", {"lon": 180, "lat": 90}, None),
        ("default", "181,90", None),
        ("default", "0,91", None),
        ("default", "string", None),
        ("default", 1, None),
        ("default", "3.14", None),
        ("default", "", None),
        ("array", (180, 90), (180, 90)),
        ("array", [180, 90], (180, 90)),
        ("array", "[180, -90]", (180, -90)),
        #  ('array', {'lon': 180, 'lat': 90}, None),
        ("array", [181, 90], None),
        ("array", [0, 91], None),
        ("array", "180,90", None),
        ("array", "string", None),
        ("array", 1, None),
        ("array", "3.14", None),
        ("array", "", None),
        #  ('object', {'lon': 180, 'lat': 90}, (180, 90)),
        ("object", '{"lon": 180, "lat": 90}', (180, 90)),
        ("object", "[180, -90]", None),
        ("object", {"lon": 181, "lat": 90}, None),
        ("object", {"lon": 180, "lat": -91}, None),
        #  ('object', [180, -90], None),
        ("object", "180,90", None),
        ("object", "string", None),
        ("object", 1, None),
        ("object", "3.14", None),
        ("object", "", None),
    ],
)
def test_geopoint_read_cell(format, source, target):
    field = Field.from_descriptor({"name": "name", "type": "geopoint", "format": format})
    cell, notes = field.read_cell(source)
    assert cell == target


@pytest.mark.parametrize("format", ["array", "object"])
@pytest.mark.parametrize(
    "lon, lat",
    [
        ("0", "0"),
        ("180", "-90"),
        ("1.1", "-2.2"),
        ("1.123456789012345678901", "-0.000000000000000000001"),
        ("1E-20", "-2E-20"),
    ],
)
def test_geopoint_json_read_write_roundtrip(format, lon, lat):
    field = Field.from_descriptor({"name": "point", "type": "geopoint", "format": format})
    source = f"[{lon}, {lat}]" if format == "array" else f'{{"lon": {lon}, "lat": {lat}}}'
    cell, notes = field.read_cell(source)
    assert notes is None
    assert cell == (Decimal(lon), Decimal(lat))
    written, notes = field.write_cell(cell)
    assert notes is None
    payload = json.loads(written, parse_float=Decimal, parse_int=Decimal)
    coordinates = payload if format == "array" else [payload["lon"], payload["lat"]]
    assert coordinates == [Decimal(lon), Decimal(lat)]
    assert all(isinstance(value, Decimal) for value in coordinates)
    assert field.read_cell(written) == (cell, None)


@pytest.mark.parametrize("format", ["array", "object"])
def test_geopoint_native_json_enum_roundtrip(format):
    coordinates = [1.1, -2.2] if format == "array" else {"lon": 1.1, "lat": -2.2}
    field = Field.from_descriptor(
        {
            "name": "point",
            "type": "geopoint",
            "format": format,
            "constraints": {"enum": [coordinates]},
        }
    )
    cell, notes = field.read_cell(coordinates)
    assert notes is None
    assert cell == (Decimal("1.1"), Decimal("-2.2"))
    assert coordinates == (
        [1.1, -2.2] if format == "array" else {"lon": 1.1, "lat": -2.2}
    )
    written, notes = field.write_cell(cell)
    assert notes is None
    assert field.read_cell(written) == (cell, None)


def test_geopoint_default_format_preserves_decimal_coordinates():
    field = Field.from_descriptor({"name": "point", "type": "geopoint"})
    cell, notes = field.read_cell("1.1,-2.2")
    assert notes is None
    assert field.write_cell(cell) == ("1.1,-2.2", None)
