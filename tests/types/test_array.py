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
        ("default", '["val1", "val2"]', [None, None], {"arrayItem": {"type": "integer"}}),
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


def test_array_read_cell_array_item():
    field = Field(type="array", array_item={"type": "integer"})
    cell, notes = field.read_cell('["1", "2", "3"]')
    assert cell == [1, 2, 3]
    assert notes is None


def test_array_read_cell_array_item_type_error():
    field = Field(type="array", array_item={"type": "integer"})
    cell, notes = field.read_cell('["1", "2", "bad"]')
    assert cell == [1, 2, None]
    assert notes == {"type": 'array item type is "integer/default"'}


def test_array_read_cell_array_item_with_constraint():
    field = Field(type="array", array_item={"constraints": {"enum": ["val1", "val2"]}})
    cell, notes = field.read_cell('["val1", "val2"]')
    assert cell == ["val1", "val2"]
    assert notes is None


def test_array_read_cell_array_item_with_constraint_error():
    field = Field(type="array", array_item={"constraints": {"enum": ["val1"]}})
    cell, notes = field.read_cell('["val1", "val2"]')
    assert cell == ["val1", "val2"]
    assert notes == {"enum": 'array item constraint "enum" is "[\'val1\']"'}
