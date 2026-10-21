"""Validation of Well-Known Text (WKT) geometries

The supported syntax follows the BNF of the OGC Simple Feature Access standard
(OGC 06-103r4, section 7.2): the structure is checked by recursive descent, and
the coordinate lists, which make up nearly all of the text, by a single regular
expression.
"""

from __future__ import annotations

import re
from typing import Callable, Dict

NUMBER = r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?"

Rule = Callable[[str, int], int]
"""A rule matches the text at a position and returns the end position or -1"""


def is_wkt(text: str) -> bool:
    """Check if a text is a WKT geometry"""
    pos = geometry(text, 0)
    if pos < 0:
        return False
    return SPACE_RE.match(text, pos).end() == len(text)  # type: ignore


# Tokens

SPACE_RE = re.compile(r"\s*")

# A keyword must not be followed by a letter or digit: "POINTZ" isn't "POINT Z"
WORD_RE = re.compile(r"\s*([^\W_]+)")

DIMENSIONS = ("Z", "M", "ZM")


def coordinates_re(*, many: bool) -> re.Pattern[str]:
    groups = iter(range(1, 100))

    # Numbers are matched atomically: "(?=(N))\1" works on Python < 3.11 too
    def number() -> str:
        return rf"(?=({NUMBER}))\{next(groups)}"

    # Coordinates are separated by whitespace: "1-2" isn't "1 -2"
    def point() -> str:
        return rf"\s*{number()}\s+{number()}(?:\s+{number()})?(?:\s+{number()})?"

    # Groups are numbered by position, so the first point must be built first
    first = point()
    more = rf"(?:\s*,{point()})*" if many else ""
    return re.compile(rf"\s*\({first}{more}\s*\)")


POINT_RE = coordinates_re(many=False)
POINTS_RE = coordinates_re(many=True)


def word(text: str, pos: int):
    match = WORD_RE.match(text, pos)
    if match is None:
        return None, pos
    return match.group(1), match.end()


def char(text: str, pos: int, char: str) -> int:
    pos = SPACE_RE.match(text, pos).end()  # type: ignore
    return pos + 1 if text.startswith(char, pos) else -1


def empty(text: str, pos: int) -> int:
    value, end = word(text, pos)
    return end if value == "EMPTY" else -1


# Rules


def geometry(text: str, pos: int) -> int:
    value, pos = word(text, pos)
    rule = GEOMETRIES.get(value) if value else None
    if rule is None:
        return -1
    return rule(text, dimensions(text, pos))


def dimensions(text: str, pos: int) -> int:
    value, end = word(text, pos)
    return end if value in DIMENSIONS else pos


def tagged(keyword: str, rule: Rule) -> Rule:
    def parse(text: str, pos: int) -> int:
        value, pos = word(text, pos)
        if value != keyword:
            return -1
        return rule(text, dimensions(text, pos))

    return parse


def list_of(item: Rule) -> Rule:
    def parse(text: str, pos: int) -> int:
        end = empty(text, pos)
        if end >= 0:
            return end
        pos = char(text, pos, "(")
        if pos < 0:
            return -1
        pos = item(text, pos)
        while pos >= 0:
            end = char(text, pos, ",")
            if end < 0:
                return char(text, pos, ")")
            pos = item(text, end)
        return -1

    return parse


def point_text(text: str, pos: int) -> int:
    end = empty(text, pos)
    if end >= 0:
        return end
    match = POINT_RE.match(text, pos)
    return match.end() if match else -1


def linestring_text(text: str, pos: int) -> int:
    end = empty(text, pos)
    if end >= 0:
        return end
    match = POINTS_RE.match(text, pos)
    return match.end() if match else -1


def triangle_text(text: str, pos: int) -> int:
    end = empty(text, pos)
    if end >= 0:
        return end
    pos = char(text, pos, "(")
    if pos < 0:
        return -1
    pos = linestring_text(text, pos)
    if pos < 0:
        return -1
    return char(text, pos, ")")


def single_curve_text(text: str, pos: int) -> int:
    end = linestring_text(text, pos)
    if end >= 0:
        return end
    return circularstring(text, pos)


def curve_text(text: str, pos: int) -> int:
    end = single_curve_text(text, pos)
    if end >= 0:
        return end
    return compoundcurve(text, pos)


def surface_text(text: str, pos: int) -> int:
    value, end = word(text, pos)
    if value == "CURVEPOLYGON":
        return curvepolygon_text(text, end)
    return polygon_text(text, pos)


circularstring = tagged("CIRCULARSTRING", linestring_text)
compoundcurve_text = list_of(single_curve_text)
compoundcurve = tagged("COMPOUNDCURVE", compoundcurve_text)
curvepolygon_text = list_of(curve_text)
polygon_text = list_of(linestring_text)

GEOMETRIES: Dict[str, Rule] = {
    "POINT": point_text,
    "LINESTRING": linestring_text,
    "CIRCULARSTRING": linestring_text,
    "COMPOUNDCURVE": compoundcurve_text,
    "CURVEPOLYGON": curvepolygon_text,
    "POLYGON": polygon_text,
    "TRIANGLE": triangle_text,
    "MULTIPOINT": list_of(point_text),
    "MULTICURVE": list_of(curve_text),
    "MULTILINESTRING": list_of(linestring_text),
    "MULTISURFACE": list_of(surface_text),
    "MULTIPOLYGON": list_of(polygon_text),
    "POLYHEDRALSURFACE": list_of(polygon_text),
    "TIN": list_of(triangle_text),
    "GEOMETRYCOLLECTION": list_of(geometry),
}
