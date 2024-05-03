from datetime import datetime

import pytest
from dateutil import tz

from frictionless import Field

# General


@pytest.mark.parametrize(
    "format, source, target",
    [
        ("default", datetime(2014, 1, 1, 6), datetime(2014, 1, 1, 6)),
        ("default", "2014-01-01T06:00:00", datetime(2014, 1, 1, 6)),
        ("default", "2014-01-01T06:00:00Z", datetime(2014, 1, 1, 6, tzinfo=tz.tzutc())),
        (
            "default",
            "2014-01-01T06:00:00+01:00",
            datetime(2014, 1, 1, 6, tzinfo=tz.tzoffset("BST", 3600)),
        ),
        ("default", "2014-01-01T06:00:00+1:00", None),
        ("default", "Mon 1st Jan 2014 9 am", None),
        ("default", "invalid", None),
        ("default", True, None),
        ("default", "", None),
        ("any", datetime(2014, 1, 1, 6), datetime(2014, 1, 1, 6)),
        ("any", "2014-01-01T06:00:00", datetime(2014, 1, 1, 6)),
        ("any", "2014-01-01T06:00:00Z", datetime(2014, 1, 1, 6, tzinfo=tz.tzutc())),
        ("any", "10th Jan 1969 9 am", datetime(1969, 1, 10, 9)),
        ("any", "invalid", None),
        ("any", True, None),
        ("any", "", None),
        (
            "%d/%m/%y %H:%M",
            datetime(2006, 11, 21, 16, 30),
            datetime(2006, 11, 21, 16, 30),
        ),
        ("%d/%m/%y %H:%M", "21/11/06 16:30", datetime(2006, 11, 21, 16, 30)),
        ("%H:%M %d/%m/%y", "21/11/06 16:30", None),
        ("%d/%m/%y %H:%M", "invalid", None),
        ("%d/%m/%y %H:%M", True, None),
        ("%d/%m/%y %H:%M", "", None),
        ("invalid", "21/11/06 16:30", None),
        # Deprecated
        (
            "fmt:%d/%m/%y %H:%M",
            datetime(2006, 11, 21, 16, 30),
            datetime(2006, 11, 21, 16, 30),
        ),
        ("fmt:%d/%m/%y %H:%M", "21/11/06 16:30", datetime(2006, 11, 21, 16, 30)),
        ("fmt:%H:%M %d/%m/%y", "21/11/06 16:30", None),
        ("fmt:%d/%m/%y %H:%M", "invalid", None),
        ("fmt:%d/%m/%y %H:%M", True, None),
        ("fmt:%d/%m/%y %H:%M", "", None),
    ],
)
def test_datetime_read_cell(format, source, target, recwarn):
    field = Field.from_descriptor({"name": "name", "type": "datetime", "format": format})
    cell, notes = field.read_cell(source)
    assert cell == target
    if not format.startswith("fmt:"):
        assert recwarn.list == []
