import pytest

from frictionless import Field, Package, fields

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
    field = Field.from_descriptor(descriptor)
    cell = field.read_cell(source)[0]
    assert cell == target


# Array Item


def test_array_read_cell_array_item():
    field = fields.ArrayField(name="name", array_item={"type": "integer"})
    cell, notes = field.read_cell('["1", "2", "3"]')
    assert cell == [1, 2, 3]
    assert notes is None


def test_array_read_cell_array_item_type_error():
    field = fields.ArrayField(name="name", array_item={"type": "integer"})
    cell, notes = field.read_cell('["1", "2", "bad"]')
    assert cell == [1, 2, None]
    assert notes == {"type": 'array item type is "integer/default"'}


def test_array_read_cell_array_item_with_constraint():
    field = fields.ArrayField(
        name="name", array_item={"constraints": {"enum": ["val1", "val2"]}}
    )
    cell, notes = field.read_cell('["val1", "val2"]')
    assert cell == ["val1", "val2"]
    assert notes is None


def test_array_read_cell_array_item_with_constraint_error():
    field = fields.ArrayField(name="name", array_item={"constraints": {"enum": ["val1"]}})
    cell, notes = field.read_cell('["val1", "val2"]')
    assert cell == ["val1", "val2"]
    assert notes == {"enum": 'array item constraint "enum" is "[\'val1\']"'}


# Bugs


def test_array_unhashable_type_list_issue_1293():
    package = Package("data/issue-1293/datapackage.json")
    assert package.get_table_resource("sample").read_rows() == [
        {"field": ["aaa", "bbb"]},
        {"field": []},
    ]
