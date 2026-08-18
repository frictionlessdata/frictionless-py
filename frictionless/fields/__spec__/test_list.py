import datetime
from decimal import Decimal

import pytest

from frictionless import Field, FrictionlessException, Resource, Schema, fields

# General


@pytest.mark.parametrize(
    "source, target, options",
    [
        ("value1,value2", ["value1", "value2"], {}),
        ("value1", ["value1"], {}),
        ("value1,,value3", ["value1", "", "value3"], {}),
        (["value1", "value2"], ["value1", "value2"], {}),
        (("value1", "value2"), ["value1", "value2"], {}),
        (1, None, {}),
        ({"key": "value"}, None, {}),
        ("1,2,3", [1, 2, 3], {"itemType": "integer"}),
        ("1,2,", None, {"itemType": "integer"}),
        ("1,bad,3", None, {"itemType": "integer"}),
        ("1.5,2", [Decimal("1.5"), Decimal("2")], {"itemType": "number"}),
        ("true,false", [True, False], {"itemType": "boolean"}),
        ("2  ,  3", [2, 3], {"itemType": "integer"}),
        ("value1;value2", ["value1", "value2"], {"delimiter": ";"}),
        ("value1||value2", ["value1", "value2"], {"delimiter": "||"}),
        ("value1;value2", ["value1;value2"], {}),
    ],
)
def test_list_read_cell(source, target, options):
    descriptor = {"name": "name", "type": "list"}
    descriptor.update(options)
    field = Field.from_descriptor(descriptor)
    cell = field.read_cell(source)[0]
    assert cell == target


def test_list_read_cell_type_error_note():
    field = fields.ListField(name="name", item_type="integer")
    cell, notes = field.read_cell("1,bad,3")
    assert cell is None
    assert notes == {"type": 'type is "list/default"'}


# Item Type


@pytest.mark.parametrize(
    "item_type, source, target",
    [
        ("string", "a,b", ["a", "b"]),
        ("integer", "1,2", [1, 2]),
        ("boolean", "true,false", [True, False]),
        ("number", "1.5,2.5", [Decimal("1.5"), Decimal("2.5")]),
        ("date", "2006-11-21", [datetime.date(2006, 11, 21)]),
        ("time", "06:00:00", [datetime.time(6)]),
        (
            "datetime",
            "2006-11-21T16:30:00",
            [datetime.datetime(2006, 11, 21, 16, 30)],
        ),
    ],
)
def test_list_read_cell_item_type(item_type, source, target):
    field = fields.ListField(name="name", item_type=item_type)
    cell, notes = field.read_cell(source)
    assert cell == target
    assert notes is None


def test_list_read_cell_item_type_default_format_only():
    # The standard requires items in the default form of their type
    field = fields.ListField(name="name", item_type="date")
    assert field.read_cell("21/11/2006")[0] is None


# Missing Values


def test_list_read_cell_missing_value():
    field = fields.ListField(name="name")
    assert field.read_cell("")[0] is None


def test_list_read_cell_missing_value_is_not_an_item():
    field = fields.ListField(name="name", item_type="integer", missing_values=["-"])
    assert field.read_cell("-")[0] is None
    assert field.read_cell("1,-,3")[0] is None


# Constraints


def test_list_read_cell_required():
    field = fields.ListField(name="name", constraints={"required": True})
    cell, notes = field.read_cell("")
    assert cell is None
    assert notes == {"required": 'constraint "required" is "True"'}


def test_list_read_cell_min_length():
    field = fields.ListField(name="name", constraints={"minLength": 2})
    assert field.read_cell("a,b")[1] is None
    assert field.read_cell("a")[1] == {"minLength": 'constraint "minLength" is "2"'}


def test_list_read_cell_max_length():
    field = fields.ListField(name="name", constraints={"maxLength": 2})
    assert field.read_cell("a,b")[1] is None
    assert field.read_cell("a,b,c")[1] == {"maxLength": 'constraint "maxLength" is "2"'}


def test_list_read_cell_enum():
    field = fields.ListField(
        name="name", item_type="integer", constraints={"enum": ["1,2"]}
    )
    assert field.read_cell("1,2")[1] is None
    assert field.read_cell("1,3")[1] == {"enum": 'constraint "enum" is "[\'1,2\']"'}


def test_list_read_cell_unsupported_constraint():
    with pytest.raises(FrictionlessException) as excinfo:
        Field.from_descriptor(
            {"name": "name", "type": "list", "constraints": {"pattern": "a.*"}}
        )
    reasons = excinfo.value.reasons
    assert reasons[0].type == "field-error"
    assert reasons[0].note == 'constraint "pattern" is not supported by type "list"'


# Write


@pytest.mark.parametrize(
    "source, target, options",
    [
        (["value1", "value2"], "value1,value2", {}),
        ([1, 2, 3], "1,2,3", {"itemType": "integer"}),
        (["value1", "value2"], "value1;value2", {"delimiter": ";"}),
        ([], "", {}),
    ],
)
def test_list_write_cell(source, target, options):
    descriptor = {"name": "name", "type": "list"}
    descriptor.update(options)
    field = Field.from_descriptor(descriptor)
    assert field.write_cell(source)[0] == target


def test_list_write_cell_round_trip():
    field = fields.ListField(name="name", item_type="integer", delimiter=";")
    assert field.read_cell(field.write_cell([1, 2, 3])[0])[0] == [1, 2, 3]


# Metadata


def test_list_metadata_defaults():
    field = Field.from_descriptor({"name": "name", "type": "list"})
    assert field.delimiter == ","
    assert field.item_type == "string"


def test_list_metadata_item_type_must_be_a_standard_type():
    with pytest.raises(FrictionlessException) as excinfo:
        Field.from_descriptor({"name": "name", "type": "list", "itemType": "geopoint"})
    reasons = excinfo.value.reasons
    assert reasons[0].type == "field-error"
    assert reasons[0].note.count("'geopoint' is not one of")


def test_list_metadata_export():
    field = fields.ListField(name="name", item_type="integer", delimiter=";")
    assert field.to_descriptor() == {
        "name": "name",
        "type": "list",
        "itemType": "integer",
        "delimiter": ";",
    }


# Schema


def test_list_schema_from_descriptor_issue_1741():
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "codes", "type": "list", "itemType": "integer"},
            ]
        }
    )
    assert schema.get_field("codes").item_type == "integer"


def test_list_resource_read_rows():
    resource = Resource(
        data=[["id", "codes"], ["1", "11,22"], ["2", "33"]],
        schema=Schema.from_descriptor(
            {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "codes", "type": "list", "itemType": "integer"},
                ]
            }
        ),
    )
    assert resource.read_rows() == [
        {"id": 1, "codes": [11, 22]},
        {"id": 2, "codes": [33]},
    ]
