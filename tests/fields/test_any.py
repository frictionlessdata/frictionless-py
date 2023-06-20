import pytest

from frictionless import Field

# General


@pytest.mark.parametrize(
    "format, source, target",
    [
        ("default", 1, 1),
        ("default", "1", "1"),
        ("default", "3.14", "3.14"),
        ("default", True, True),
        ("default", "", None),
    ],
)
def test_any_read_cell(format, source, target):
    field = Field.from_descriptor({"name": "name", "type": "any", "format": format})
    cell, notes = field.read_cell(source)
    assert cell == target
