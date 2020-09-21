import pytest
from frictionless import Field


# General


@pytest.mark.parametrize(
    "format, source, target",
    [
        ("default", [], []),
        ("default", (), []),
        ("default", "[]", []),
        ("default", ["key", "value"], ["key", "value"]),
        ("default", ("key", "value"), ["key", "value"]),
        ("default", '["key", "value"]', ["key", "value"]),
        ("default", {"key": "value"}, None),
        ("default", '{"key": "value"}', None),
        ("default", "string", None),
        ("default", 1, None),
        ("default", "3.14", None),
        ("default", "", None),
    ],
)
def test_array_read_cell(format, source, target):
    field = Field({"name": "name", "type": "array", "format": format})
    cell, notes = field.read_cell(source)
    assert cell == target
