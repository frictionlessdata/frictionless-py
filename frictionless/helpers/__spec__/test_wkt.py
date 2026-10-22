import pytest

from frictionless.helpers.wkt import is_wkt


@pytest.mark.parametrize(
    "text,valid",
    [
        # Whitespace
        ("POINT(1 2)", True),
        ("  POINT ( 1  2 )  ", True),
        ("POINT\t(1\n2)\n", True),
        ("POINT (1 2)", True),
        # Numbers
        ("POINT (1e5 2E-3)", True),
        ("POINT (.5 5.)", True),
        ("POINT (+1 -2)", True),
        ("POINT (１ 2)", False),
        ("POINT (1 2e)", False),
        # Coordinates must be separated by whitespace
        ("POINT (1-2)", False),
        ("POINT (1.5.5)", False),
        ("LINESTRING (0 0, 1 1-2)", False),
        # Numbers are never split: "12" isn't "1 2"
        ("POINT (12)", False),
        ("POINT (1.5)", False),
        ("POINT (123)", False),
        # Dimensions
        ("POINT (1)", False),
        ("POINT (1 2 3 4)", True),
        ("POINT (1 2 3 4 5)", False),
        ("POINT Z (1 2 3)", True),
        ("POINT Z(1 2 3)", True),
        ("POINT ZM (1 2 3 4)", True),
        ("POINT Z EMPTY", True),
        # Keywords
        ("POINTZ (1 2 3)", False),
        ("POINT ZMEMPTY", False),
        ("POINT EMPTYX", False),
        ("POINT1 (1 2)", False),
        ("point (1 2)", False),
        # Lists
        ("LINESTRING (1 2)", True),
        ("LINESTRING (1 2,)", False),
        ("LINESTRING ()", False),
        ("LINESTRING EMPTY", True),
        ("POLYGON (EMPTY)", True),
        ("MULTIPOINT ((10 40), EMPTY)", True),
        ("MULTIPOINT (10 40, 40 30)", False),
        ("TRIANGLE ((0 0, 1 0), (1 1, 2 2))", False),
        # Nesting
        ("GEOMETRYCOLLECTION (GEOMETRYCOLLECTION (POINT (1 2)))", True),
        ("MULTISURFACE (CURVEPOLYGON ((0 0, 1 1)), ((0 0, 1 1)))", True),
        ("COMPOUNDCURVE (CIRCULARSTRING EMPTY, (1 2))", True),
        ("MULTICURVE ((0 0, 1 1), COMPOUNDCURVE ((0 0, 1 1)))", True),
        # Nothing must follow the geometry
        ("POINT (1 2) garbage", False),
        ("POINT (1 2)POINT (3 4)", False),
        ("POLYGON ((0 0, 1 0, 0 0)))", False),
        ("SRID=4326;POINT (1 2)", False),
        ("", False),
    ],
)
def test_is_wkt(text, valid):
    assert is_wkt(text) is valid


def test_is_wkt_large_geometry():
    ring = ", ".join(f"{i}.123456 {i}.654321" for i in range(100000))
    assert is_wkt(f"POLYGON (({ring}, 0 0))")
