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


@pytest.mark.parametrize("sequence_type", [list, tuple])
@pytest.mark.parametrize("coordinate", [0, 1])
def test_geopoint_rejects_nan_coordinate(sequence_type, coordinate):
    source = [0.0, 0.0]
    source[coordinate] = float("nan")
    field = Field.from_descriptor({"name": "point", "type": "geopoint"})
    cell, notes = field.read_cell(sequence_type(source))
    assert cell is None
    assert notes
