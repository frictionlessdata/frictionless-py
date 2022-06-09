import io
import json
import pytest
import requests
from decimal import Decimal
from frictionless import Schema, helpers
from frictionless import FrictionlessException


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"
DESCRIPTOR_MIN = {"fields": [{"name": "id"}, {"name": "height", "type": "integer"}]}
DESCRIPTOR_MAX = {
    "fields": [
        {"name": "id", "type": "string", "constraints": {"required": True}},
        {"name": "height", "type": "number"},
        {"name": "age", "type": "integer"},
        {"name": "name", "type": "string"},
        {"name": "occupation", "type": "string"},
    ],
    "primaryKey": ["id"],
    "foreignKeys": [
        {"fields": ["name"], "reference": {"resource": "", "fields": ["id"]}}
    ],
    "missingValues": ["", "-", "null"],
}


# General


def test_schema():
    assert Schema(DESCRIPTOR_MIN)
    assert Schema(DESCRIPTOR_MAX)
    assert Schema("data/schema-valid-full.json")
    assert Schema("data/schema-valid-simple.json")


def test_schema_extract_metadata_error():
    with pytest.raises(FrictionlessException):
        Schema([])


def test_schema_metadata_invalid():
    schema = Schema("data/schema-invalid-multiple-errors.json")
    assert len(schema.metadata_errors) == 5


def test_schema_descriptor():
    assert Schema(DESCRIPTOR_MIN) == DESCRIPTOR_MIN
    assert Schema(DESCRIPTOR_MAX) == DESCRIPTOR_MAX


def test_schema_descriptor_path():
    path = "data/schema-valid-simple.json"
    actual = Schema(path)
    with io.open(path, encoding="utf-8") as file:
        expect = json.load(file)
    assert actual == expect


@pytest.mark.vcr
def test_schema_descriptor_url():
    url = BASEURL % "data/schema.json"
    actual = Schema(url)
    expect = requests.get(url).json()
    assert actual == expect


def test_schema_read_cells():
    schema = Schema(DESCRIPTOR_MAX)
    source = ["string", "10.0", "1", "string", "string"]
    target = ["string", Decimal(10.0), 1, "string", "string"]
    cells, notes = schema.read_cells(source)
    assert cells == target


def test_schema_read_cells_null_values():
    schema = Schema(DESCRIPTOR_MAX)
    source = ["string", "", "-", "string", "null"]
    target = ["string", None, None, "string", None]
    cells, notes = schema.read_cells(source)
    assert cells == target


def test_schema_read_cells_too_short():
    schema = Schema(DESCRIPTOR_MAX)
    source = ["string", "10.0", "1", "string"]
    target = ["string", Decimal(10.0), 1, "string", None]
    cells, notes = schema.read_cells(source)
    assert cells == target


def test_schema_read_cells_too_long():
    schema = Schema(DESCRIPTOR_MAX)
    source = ["string", "10.0", "1", "string", "string", "string"]
    target = ["string", Decimal(10.0), 1, "string", "string"]
    cells, notes = schema.read_cells(source)
    assert cells == target


def test_schema_read_cells_wrong_type():
    schema = Schema(DESCRIPTOR_MAX)
    source = ["string", "notdecimal", "10.6", "string", "string"]
    target = ["string", None, None, "string", "string"]
    cells, notes = schema.read_cells(source)
    assert cells == target
    assert notes[1] == {"type": 'type is "number/default"'}
    assert notes[2] == {"type": 'type is "integer/default"'}


def test_schema_missing_values():
    assert Schema(DESCRIPTOR_MIN).missing_values == [""]
    assert Schema(DESCRIPTOR_MAX).missing_values == ["", "-", "null"]


def test_schema_fields():
    expect = ["id", "height"]
    actual = [field.name for field in Schema(DESCRIPTOR_MIN).fields]
    assert expect == actual


def test_schema_get_field():
    schema = Schema(DESCRIPTOR_MIN)
    assert schema.get_field("id").name == "id"
    assert schema.get_field("height").name == "height"


def test_schema_get_field_error_not_found():
    schema = Schema(DESCRIPTOR_MIN)
    with pytest.raises(FrictionlessException) as excinfo:
        schema.get_field("bad")
    error = excinfo.value.error
    assert error.code == "schema-error"
    assert error.note == 'field "bad" does not exist'


def test_schema_update_field():
    schema = Schema(DESCRIPTOR_MIN)
    schema.get_field("id")["type"] = "number"
    schema.get_field("height")["type"] = "number"
    assert schema.get_field("id").type == "number"
    assert schema.get_field("height").type == "number"


def test_schema_has_field():
    schema = Schema(DESCRIPTOR_MIN)
    assert schema.has_field("id")
    assert schema.has_field("height")
    assert not schema.has_field("undefined")


def test_schema_remove_field():
    schema = Schema(DESCRIPTOR_MIN)
    assert schema.remove_field("height")
    assert schema.field_names == ["id"]


def test_schema_remove_field_error_not_found():
    schema = Schema(DESCRIPTOR_MIN)
    with pytest.raises(FrictionlessException) as excinfo:
        schema.remove_field("bad")
    error = excinfo.value.error
    assert error.code == "schema-error"
    assert error.note == 'field "bad" does not exist'


def test_schema_field_names():
    assert Schema(DESCRIPTOR_MIN).field_names == ["id", "height"]


def test_schema_primary_key():
    assert Schema(DESCRIPTOR_MIN).primary_key == []
    assert Schema(DESCRIPTOR_MAX).primary_key == ["id"]


def test_schema_foreign_keys():
    assert Schema(DESCRIPTOR_MIN).foreign_keys == []
    assert Schema(DESCRIPTOR_MAX).foreign_keys == DESCRIPTOR_MAX["foreignKeys"]


def test_schema_add_then_remove_field():
    schema = Schema()
    schema.add_field({"name": "name"})
    field = schema.remove_field("name")
    assert field.name == "name"


def test_schema_primary_foreign_keys_as_array():
    descriptor = {
        "fields": [{"name": "name"}],
        "primaryKey": ["name"],
        "foreignKeys": [
            {
                "fields": ["parent_id"],
                "reference": {"resource": "resource", "fields": ["id"]},
            }
        ],
    }
    schema = Schema(descriptor)
    assert schema.primary_key == ["name"]
    assert schema.foreign_keys == [
        {"fields": ["parent_id"], "reference": {"resource": "resource", "fields": ["id"]}}
    ]


def test_schema_primary_foreign_keys_as_string():
    descriptor = {
        "fields": [{"name": "name"}],
        "primaryKey": "name",
        "foreignKeys": [
            {"fields": "parent_id", "reference": {"resource": "resource", "fields": "id"}}
        ],
    }
    schema = Schema(descriptor)
    assert schema.primary_key == ["name"]
    assert schema.foreign_keys == [
        {"fields": ["parent_id"], "reference": {"resource": "resource", "fields": ["id"]}}
    ]


def test_schema_metadata_valid():
    assert Schema("data/schema-valid-simple.json").metadata_valid
    assert Schema("data/schema-valid-full.json").metadata_valid
    assert Schema("data/schema-valid-pk-array.json").metadata_valid
    assert Schema("data/schema-valid-fk-array.json").metadata_valid


def test_schema_metadata_not_valid():
    assert not Schema("data/schema-invalid-empty.json").metadata_valid
    assert not Schema("data/schema-invalid-pk-string.json").metadata_valid
    assert not Schema("data/schema-invalid-pk-array.json").metadata_valid
    assert not Schema("data/schema-invalid-fk-string.json").metadata_valid
    assert not Schema("data/schema-invalid-fk-no-reference.json").metadata_valid
    assert not Schema("data/schema-invalid-fk-array.json").metadata_valid
    assert not Schema("data/schema-invalid-fk-string-array-ref.json").metadata_valid
    assert not Schema("data/schema-invalid-fk-array-string-ref.json").metadata_valid


def test_schema_metadata_not_valid_multiple_errors():
    schema = Schema("data/schema-invalid-multiple-errors.json")
    assert len(schema.metadata_errors) == 5


def test_schema_metadata_not_valid_multiple_errors_with_pk():
    schema = Schema("data/schema-invalid-pk-is-wrong-type.json")
    assert len(schema.metadata_errors) == 3


def test_schema_metadata_error_message():
    schema = Schema({"fields": [{"name": "name", "type": "other"}]})
    note = schema.metadata_errors[0]["note"]
    assert len(schema.metadata_errors) == 1
    assert "is not valid" in note
    assert "{'name': 'name', 'type': 'other'}" in note
    assert "is not valid under any of the given schema" in note


def test_schema_valid_examples():
    schema = Schema(
        {
            "fields": [
                {"name": "name", "type": "string", "example": "John"},
                {"name": "age", "type": "integer", "example": 42},
            ]
        }
    )
    assert schema.get_field("name").example == "John"
    assert len(schema.metadata_errors) == 0


def test_schema_invalid_example():
    schema = Schema(
        {
            "fields": [
                {
                    "name": "name",
                    "type": "string",
                    "example": None,
                    "constraints": {"required": True},
                }
            ]
        }
    )
    note = schema.metadata_errors[0]["note"]
    assert len(schema.metadata_errors) == 1
    assert 'example value for field "name" is not valid' == note


@pytest.mark.parametrize("create_descriptor", [(False,), (True,)])
def test_schema_standard_specs_properties(create_descriptor):
    options = dict(
        fields=[],
        missing_values=[],
        primary_key=[],
        foreign_keys=[],
    )
    schema = (
        Schema(**options)
        if not create_descriptor
        else Schema(helpers.create_descriptor(**options))
    )
    assert schema.fields == []
    assert schema.missing_values == []
    assert schema.primary_key == []
    assert schema.foreign_keys == []


# Issues


def test_schema_field_date_format_issue_177():
    descriptor = {"fields": [{"name": "myfield", "type": "date", "format": "%d/%m/%y"}]}
    schema = Schema(descriptor)
    assert schema


def test_schema_field_time_format_issue_177():
    descriptor = {"fields": [{"name": "myfield", "type": "time", "format": "%H:%M:%S"}]}
    schema = Schema(descriptor)
    assert schema


def test_schema_add_remove_field_issue_218():
    descriptor = {
        "fields": [
            {"name": "test_1", "type": "string", "format": "default"},
            {"name": "test_2", "type": "string", "format": "default"},
            {"name": "test_3", "type": "string", "format": "default"},
        ]
    }
    test_schema = Schema(descriptor)
    test_schema.remove_field("test_1")
    test_schema.add_field({"name": "test_4", "type": "string", "format": "default"})


def test_schema_not_supported_type_issue_goodatbles_304():
    schema = Schema({"fields": [{"name": "name"}, {"name": "age", "type": "bad"}]})
    assert schema.metadata_valid is False
    assert schema.fields[1] == {"name": "age", "type": "bad"}


def test_schema_summary():
    schema = Schema(DESCRIPTOR_MAX)
    output = schema.to_summary()
    assert (
        output.count("| name       | type    | required   |")
        and output.count("| id         | string  | True       |")
        and output.count("| height     | number  |            |")
        and output.count("| age        | integer |            |")
        and output.count("| name       | string  |            |")
    )


def test_schema_summary_without_required():
    descriptor = {
        "fields": [
            {"name": "test_1", "type": "string", "format": "default"},
            {"name": "test_2", "type": "string", "format": "default"},
            {"name": "test_3", "type": "string", "format": "default"},
        ]
    }
    schema = Schema(descriptor)
    output = schema.to_summary()
    assert (
        output.count("| name   | type   | required   |")
        and output.count("| test_1 | string |            |")
        and output.count("| test_2 | string |            |")
        and output.count("| test_3 | string |            |")
    )


def test_schema_summary_without_type_missing_for_some_fields():
    descriptor = {
        "fields": [
            {"name": "id", "format": "default"},
            {"name": "name", "type": "string", "format": "default"},
            {"name": "age", "format": "default"},
        ]
    }
    schema = Schema(descriptor)
    output = schema.to_summary()
    assert (
        output.count("| name   | type   | required   |")
        and output.count("| id     | any    |            |")
        and output.count("| name   | string |            |")
        and output.count("| age    | any    |            |")
    )


def test_schema_summary_with_name_missing_for_some_fields():
    descriptor = {
        "fields": [
            {"type": "int", "format": "default"},
            {"type": "int", "format": "default"},
            {"name": "name", "type": "string", "format": "default"},
        ]
    }
    schema = Schema(descriptor)
    output = schema.to_summary()
    assert (
        output.count("| name   | type   | required   |")
        and output.count("| int    | int    |            |")
        and output.count("| int    | int    |            |")
        and output.count("| name   | string |            |")
    )
