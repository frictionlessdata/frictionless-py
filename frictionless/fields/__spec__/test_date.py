from datetime import date, datetime

import pytest

from frictionless import Field

# General


@pytest.mark.parametrize(
    "format, source, target",
    [
        ("default", date(2019, 1, 1), date(2019, 1, 1)),
        ("default", "2019-01-01", date(2019, 1, 1)),
        ("default", "10th Jan 1969", None),
        ("default", "invalid", None),
        ("default", True, None),
        ("default", "", None),
        ("default", datetime(2018, 1, 1), date(2018, 1, 1)),
        ("default", datetime(2018, 3, 1, 8, 30, 23), None),
        ("any", date(2019, 1, 1), date(2019, 1, 1)),
        ("any", "2019-01-01", date(2019, 1, 1)),
        ("any", "10th Jan 1969", date(1969, 1, 10)),
        ("any", "10th Jan nineteen sixty nine", None),
        ("any", "invalid", None),
        ("any", True, None),
        ("any", "", None),
        ("%d/%m/%y", date(2019, 1, 1), date(2019, 1, 1)),
        ("%d/%m/%y", "21/11/06", date(2006, 11, 21)),
        ("%y/%m/%d", "21/11/06 16:30", None),
        ("%d/%m/%y", "invalid", None),
        ("%d/%m/%y", True, None),
        ("%d/%m/%y", "", None),
        ("invalid", "21/11/06 16:30", None),
        # Deprecated
        ("fmt:%d/%m/%y", date(2019, 1, 1), date(2019, 1, 1)),
        ("fmt:%d/%m/%y", "21/11/06", date(2006, 11, 21)),
        ("fmt:%y/%m/%d", "21/11/06 16:30", None),
        ("fmt:%d/%m/%y", "invalid", None),
        ("fmt:%d/%m/%y", True, None),
        ("fmt:%d/%m/%y", "", None),
    ],
)
def test_date_read_cell(format, source, target, recwarn):
    field = Field.from_descriptor({"name": "name", "type": "date", "format": format})
    cell, notes = field.read_cell(source)
    assert cell == target
    if not format.startswith("fmt:"):
        assert recwarn.list == []
