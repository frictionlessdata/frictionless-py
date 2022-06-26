import pytest
from frictionless import Field2, fields


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
        ("default", {"key": "value"}, None, {}),
        ("default", '{"key": "value"}', None, {}),
        ("default", "string", None, {}),
        ("default", 1, None, {}),
        ("default", "3.14", None, {}),
        ("default", "", None, {}),
    ],
)
def test_array_read_cell(format, source, target, options):
    descriptor = {"name": "name", "type": "array", "format": format}
    descriptor.update(options)
    field = Field2.from_descriptor(descriptor)
    cell, notes = field.read_cell(source)
    assert cell == target


# Array Item


def test_array_read_cell_array_item():
    field = fields.ArrayField(array_item={"type": "integer"})
    cell, notes = field.read_cell('["1", "2", "3"]')
    assert cell == [1, 2, 3]
    assert notes == {}


def test_array_read_cell_array_item_type_error():
    field = fields.ArrayField(array_item={"type": "integer"})
    cell, notes = field.read_cell('["1", "2", "bad"]')
    assert cell == [1, 2, None]
    assert notes == {"type": 'array item type is "integer/default"'}


def test_array_read_cell_array_item_with_constraint():
    field = fields.ArrayField(array_item={"constraints": {"enum": ["val1", "val2"]}})
    cell, notes = field.read_cell('["val1", "val2"]')
    assert cell == ["val1", "val2"]
    assert notes == {}


def test_array_read_cell_array_item_with_constraint_error():
    field = fields.ArrayField(array_item={"constraints": {"enum": ["val1"]}})
    cell, notes = field.read_cell('["val1", "val2"]')
    assert cell == ["val1", "val2"]
    assert notes == {"enum": 'array item constraint "enum" is "[\'val1\']"'}
