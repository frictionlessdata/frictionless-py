import pytest

from frictionless import Field

# General


@pytest.mark.parametrize(
    "format, source, target",
    [
        ("default", "string", "string"),
        ("default", "", None),
        ("default", 0, None),
        ("uri", "http://google.com", "http://google.com"),
        ("uri", "://no-scheme.test", None),
        ("uri", "string", None),
        ("uri", "", None),
        ("uri", 0, None),
        ("email", "name@gmail.com", "name@gmail.com"),
        ("email", "http://google.com", None),
        ("email", "string", None),
        ("email", "", None),
        ("email", 0, None),
        ("binary", "dGVzdA==", "dGVzdA=="),
        ("binary", "", None),
        ("binary", "string", None),
        ("binary", 0, None),
    ],
)
def test_string_read_cell(format, source, target):
    field = Field.from_descriptor({"name": "name", "type": "string", "format": format})
    cell, _ = field.read_cell(source)
    assert cell == target


@pytest.mark.parametrize(
    "format, source, target",
    [
        ("wkt", "POINT (30 10)", "POINT (30 10)"),
        ("wkt", "LINESTRING (30 10, 10 30, 40 40)", "LINESTRING (30 10, 10 30, 40 40)"),
        (
            "wkt",
            "POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))",
            "POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))",
        ),
        (
            "wkt",
            "MULTIPOINT ((10 40), (40 30), (20 20), (30 10))",
            "MULTIPOINT ((10 40), (40 30), (20 20), (30 10))",
        ),
        (
            "wkt",
            "TRIANGLE((0 0, 1 0, 0.5 1, 0 0))",
            "TRIANGLE((0 0, 1 0, 0.5 1, 0 0))",
        ),
        (
            "wkt",
            "MULTILINESTRING ((0 0, 1 1, 2 2), (3 3, 4 4, 5 5))",
            "MULTILINESTRING ((0 0, 1 1, 2 2), (3 3, 4 4, 5 5))",
        ),
        (
            "wkt",
            "MULTIPOLYGON (((0 0, 0 1, 1 1, 1 0, 0 0)), ((1 1, 1 2, 2 2, 2 1, 1 1)))",
            "MULTIPOLYGON (((0 0, 0 1, 1 1, 1 0, 0 0)), ((1 1, 1 2, 2 2, 2 1, 1 1)))",
        ),
        (
            "wkt",
            "CIRCULARSTRING (-116.4 45.2, -118.0 47.0, -120.0 49.0)",
            "CIRCULARSTRING (-116.4 45.2, -118.0 47.0, -120.0 49.0)",
        ),
        (
            "wkt",
            "TIN (((0 0 0,0 0 1,0 1 0,0 0 0)),((0 0 0,0 1 0,1 1 0,0 0 0)))",
            "TIN (((0 0 0,0 0 1,0 1 0,0 0 0)),((0 0 0,0 1 0,1 1 0,0 0 0)))",
        ),
        (
            "wkt",
            "CURVEPOLYGON(COMPOUNDCURVE(CIRCULARSTRING (0 0,1 1,2 0),(2 0,0 0)))",
            "CURVEPOLYGON(COMPOUNDCURVE(CIRCULARSTRING (0 0,1 1,2 0),(2 0,0 0)))",
        ),
        (
            "wkt",
            "POLYHEDRALSURFACE (((0 0 0,0 0 1,0 1 1,0 1 0,0 0 0)),((0 0 0,0 1 0,1 1 0,1 0 0,0 0 0)),((0 0 0,1 0 0,1 0 1,0 0 1,0 0 0)),((1 1 0,1 1 1,1 0 1,1 0 0,1 1 0)),((0 1 0,0 1 1,1 1 1,1 1 0,0 1 0)),((0 0 1,1 0 1,1 1 1,0 1 1,0 0 1)))",
            "POLYHEDRALSURFACE (((0 0 0,0 0 1,0 1 1,0 1 0,0 0 0)),((0 0 0,0 1 0,1 1 0,1 0 0,0 0 0)),((0 0 0,1 0 0,1 0 1,0 0 1,0 0 0)),((1 1 0,1 1 1,1 0 1,1 0 0,1 1 0)),((0 1 0,0 1 1,1 1 1,1 1 0,0 1 0)),((0 0 1,1 0 1,1 1 1,0 1 1,0 0 1)))",
        ),
        ("wkt", "CIRCULARSTRING EMPTY", "CIRCULARSTRING EMPTY"),
        ("wkt", "GEOMETRYCOLLECTION EMPTY", "GEOMETRYCOLLECTION EMPTY"),
        ("wkt", "POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10)", None),
        ("wkt", "string", None),
        ("wkt", "", None),
        ("wkt", 0, None),
    ],
)
def test_string_read_cell_wkt(format, source, target):
    field = Field.from_descriptor({"name": "name", "type": "string", "format": format})
    cell, _ = field.read_cell(source)
    assert cell == target
