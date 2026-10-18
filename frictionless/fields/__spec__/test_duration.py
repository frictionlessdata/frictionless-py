import datetime

import isodate
import pytest

from frictionless import Field, Schema

# General


@pytest.mark.parametrize(
    "format, source, target",
    [
        ("default", isodate.Duration(years=1), isodate.Duration(years=1)),
        (
            "default",
            "P1Y10M3DT5H11M7S",
            isodate.Duration(years=1, months=10, days=3, hours=5, minutes=11, seconds=7),
        ),
        ("default", "P1Y", isodate.Duration(years=1)),
        ("default", "P1M", isodate.Duration(months=1)),
        ("default", "PT1S", datetime.timedelta(seconds=1)),
        ("default", datetime.timedelta(seconds=1), datetime.timedelta(seconds=1)),
        ("default", "P1M1Y", None),
        ("default", "P-1Y", None),
        ("default", "year", None),
        ("default", True, None),
        ("default", False, None),
        ("default", 1, None),
        ("default", "", None),
        ("default", [], None),
        ("default", {}, None),
    ],
)
def test_duration_read_cell(format, source, target):
    field = Field.from_descriptor({"name": "name", "type": "duration", "format": format})
    cell, notes = field.read_cell(source)
    assert cell == target


@pytest.mark.parametrize(
    "constraint, bound, source, valid",
    [
        ("minimum", "PT1S", "PT0.5S", False),
        ("minimum", "PT1S", "PT1S", True),
        ("maximum", "PT1S", "PT2S", False),
        ("maximum", "PT1S", "PT1S", True),
        ("exclusiveMinimum", "PT1S", "PT1S", False),
        ("exclusiveMinimum", "PT1S", "PT1.000001S", True),
        ("exclusiveMaximum", "PT1S", "PT1S", False),
        ("exclusiveMaximum", "PT1S", "PT0.999999S", True),
        ("minimum", "P1Y", "P12M", True),
        ("maximum", "P12M", "P1Y", True),
        ("exclusiveMinimum", "P12M", "P1Y", False),
        ("exclusiveMaximum", "P1Y", "P12M", False),
        # XML Schema's normative duration ordering examples.
        ("exclusiveMinimum", "P27D", "P1M", True),
        ("exclusiveMaximum", "P32D", "P1M", True),
        ("exclusiveMinimum", "P364D", "P1Y", True),
        ("exclusiveMaximum", "P367D", "P1Y", True),
        ("minimum", "-P2M", "-P1M", True),
        ("maximum", "-P2M", "-P1M", False),
        ("minimum", "P10000Y", "P120000M", True),
        ("exclusiveMinimum", "P10000Y", "P120001M", True),
        ("exclusiveMaximum", "-P10000Y", "-P120001M", True),
        ("minimum", "PT1S", datetime.timedelta(seconds=2), True),
        ("minimum", "P1Y", isodate.Duration(years=2), True),
        ("maximum", "not-a-duration", "PT1S", False),
    ],
)
def test_duration_bounds(constraint, bound, source, valid):
    schema = Schema.from_descriptor(
        {
            "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
            "fields": [
                {
                    "name": "duration",
                    "type": "duration",
                    "constraints": {constraint: bound},
                }
            ],
        }
    )
    field = schema.get_field("duration")
    cell, notes = field.read_cell(source)
    assert cell is not None
    assert (notes is None) == valid
    if not valid:
        assert notes == {constraint: f'constraint "{constraint}" is "{bound}"'}


@pytest.mark.parametrize(
    "constraint", ["minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"]
)
@pytest.mark.parametrize("bound", ["P28D", "P29D", "P30D", "P31D"])
def test_duration_indeterminate_bounds(constraint, bound):
    schema = Schema.from_descriptor(
        {
            "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
            "fields": [
                {
                    "name": "duration",
                    "type": "duration",
                    "constraints": {constraint: bound},
                }
            ],
        }
    )
    cell, notes = schema.get_field("duration").read_cell("P1M")
    assert cell == isodate.Duration(months=1)
    assert notes == {constraint: f'constraint "{constraint}" is "{bound}"'}


@pytest.mark.parametrize(
    "constraint", ["minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"]
)
def test_duration_bounds_missing_and_invalid_values(constraint):
    field = Field.from_descriptor(
        {"name": "duration", "type": "duration", "constraints": {constraint: "PT1S"}}
    )
    assert field.read_cell(None) == (None, None)
    assert field.read_cell("") == (None, None)
    assert field.read_cell("invalid") == (None, {"type": 'type is "duration/default"'})


@pytest.mark.parametrize(
    "constraint", ["minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"]
)
@pytest.mark.parametrize("version", [None, "1.0", "2.0"])
def test_duration_bounds_version_gate(constraint, version):
    descriptor = {
        "fields": [
            {"name": "duration", "type": "duration", "constraints": {constraint: "PT1S"}}
        ]
    }
    if version:
        descriptor["$schema"] = (
            f"https://datapackage.org/profiles/{version}/tableschema.json"
        )
    report = Schema.validate_descriptor(descriptor)
    assert report.flatten(["type", "note"]) == (
        []
        if version == "2.0"
        else [["field-error", f'constraint "{constraint}" requires datapackage v2']]
    )
