import datetime

import isodate
import pytest

from frictionless import Field

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
