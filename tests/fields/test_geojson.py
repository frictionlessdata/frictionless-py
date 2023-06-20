import pytest

from frictionless import Field

# General


@pytest.mark.parametrize(
    "format, source, target",
    [
        (
            "default",
            {"properties": {"Ã": "Ã"}, "type": "Feature", "geometry": None},
            {"properties": {"Ã": "Ã"}, "type": "Feature", "geometry": None},
        ),
        (
            "default",
            '{"geometry": null, "type": "Feature", "properties": {"\\u00c3": "\\u00c3"}}',
            {"properties": {"Ã": "Ã"}, "type": "Feature", "geometry": None},
        ),
        ("default", {"coordinates": [0, 0, 0], "type": "Point"}, None),
        ("default", "string", None),
        ("default", 1, None),
        ("default", "3.14", None),
        ("default", "", None),
        ("default", {}, None),
        ("default", "{}", None),
        (
            "topojson",
            {"type": "LineString", "arcs": [42]},
            {"type": "LineString", "arcs": [42]},
        ),
        (
            "topojson",
            '{"type": "LineString", "arcs": [42]}',
            {"type": "LineString", "arcs": [42]},
        ),
        ("topojson", "string", None),
        ("topojson", 1, None),
        ("topojson", "3.14", None),
        ("topojson", "", None),
    ],
)
def test_geojson_read_cell(format, source, target):
    field = Field.from_descriptor({"name": "name", "type": "geojson", "format": format})
    cell, notes = field.read_cell(source)
    assert cell == target
