import pytest

from frictionless import Field

# General


@pytest.mark.parametrize(
    "format, source, target",
    [
        ("default", 2000, 2000),
        ("default", "2000", 2000),
        ("default", -2000, None),
        ("default", 20000, None),
        ("default", "3.14", None),
        ("default", "", None),
    ],
)
def test_year_read_cell(format, source, target):
    field = Field.from_descriptor({"name": "name", "type": "year", "format": format})
    cell, notes = field.read_cell(source)
    assert cell == target
