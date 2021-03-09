import pytest
from frictionless import Field


# General


@pytest.mark.parametrize(
    "format, source, target, options",
    [
        ("default", [], [], {}),
        ("default", (), [], {}),
        ("default", "[]", [], {}),
        ("default", ["val1", "val2"], ["val1", "val2"], {}),
        ("default", ("val1", "val2"), ["val1", "val2"], {}),
        ("default", '["val1", "val2"]', ["val1", "val2"], {}),
        ("default", '["1", "2"]', [1, 2], {"arrayItem": {"type": "integer"}}),
        (
            "default",
            '["val1", "val2"]',
            ["val1", "val2"],
            {"arrayItem": {"constraints": {"enum": ["val1", "val2"]}}},
        ),
        ("default", '["val1", "val2"]', None, {"arrayItem": {"type": "integer"}}),
        (
            "default",
            '["val1", "val2"]',
            None,
            {"arrayItem": {"constraints": {"enum": ["val1"]}}},
        ),
        ("default", {"key": "value"}, None, {}),
        ("default", '{"key": "value"}', None, {}),
        ("default", "string", None, {}),
        ("default", 1, None, {}),
        ("default", "3.14", None, {}),
        ("default", "", None, {}),
    ],
)
def test_array_read_cell(format, source, target, options):
    field = Field(name="name", type="array", format=format)
    field.update(options)
    cell, notes = field.read_cell(source)
    assert cell == target
