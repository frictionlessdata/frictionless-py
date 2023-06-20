import pytest

from frictionless import Field

# General


@pytest.mark.parametrize(
    "format, source, target",
    [
        ("default", [2000, 10], (2000, 10)),
        ("default", (2000, 10), (2000, 10)),
        ("default", "2000-10", (2000, 10)),
        ("default", (2000, 10, 20), None),
        ("default", "2000-13-20", None),
        ("default", "2000-13", None),
        ("default", "2000-0", None),
        ("default", "13", None),
        ("default", -10, None),
        ("default", 20, None),
        ("default", "3.14", None),
        ("default", "", None),
    ],
)
def test_yearmonth_read_cell(format, source, target):
    field = Field.from_descriptor({"name": "name", "type": "yearmonth", "format": format})
    cell, notes = field.read_cell(source)
    assert cell == target
