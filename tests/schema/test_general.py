import io
import json
import pytest
import textwrap
import requests
from decimal import Decimal
from importlib import import_module
from frictionless import Schema, Field
from frictionless import FrictionlessException


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"
DESCRIPTOR_MIN = {
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "height", "type": "integer"},
    ]
}
DESCRIPTOR_MAX = {
    "fields": [
        {"name": "id", "type": "string", "constraints": {"required": True}},
        {"name": "height", "type": "number"},
        {"name": "age", "type": "integer"},
        {"name": "name", "type": "string"},
        {"name": "occupation", "type": "string"},
    ],
    "missingValues": ["", "-", "null"],
    "primaryKey": ["id"],
    "foreignKeys": [
        {"fields": ["name"], "reference": {"resource": "", "fields": ["id"]}}
    ],
}


# General


def test_schema():
    assert Schema.from_descriptor(DESCRIPTOR_MIN)
    assert Schema.from_descriptor(DESCRIPTOR_MAX)
    assert Schema.from_descriptor("data/schema-valid-full.json")
    assert Schema.from_descriptor("data/schema-valid-simple.json")


def test_schema_extract_metadata_error():
    with pytest.raises(FrictionlessException):
        Schema.from_descriptor([])  # type: ignore


def test_schema_descriptor():
    assert Schema.from_descriptor(DESCRIPTOR_MAX).to_descriptor() == DESCRIPTOR_MAX


def test_schema_descriptor_path():
    path = "data/schema-valid-simple.json"
    schema = Schema.from_descriptor(path)
    with io.open(path, encoding="utf-8") as file:
        descriptor = json.load(file)
    assert schema.to_descriptor() == descriptor


@pytest.mark.vcr
def test_schema_descriptor_url():
    url = BASEURL % "data/schema.json"
    schema = Schema.from_descriptor(url)
    descriptor = requests.get(url).json()
    assert schema.to_descriptor() == descriptor


def test_schema_read_cells():
    schema = Schema.from_descriptor(DESCRIPTOR_MAX)
    source = ["string", "10.0", "1", "string", "string"]
    target = ["string", Decimal(10.0), 1, "string", "string"]
    cells, notes = schema.read_cells(source)
    assert cells == target
    assert len(notes) == 5


def test_schema_read_cells_null_values():
    schema = Schema.from_descriptor(DESCRIPTOR_MAX)
    source = ["string", "", "-", "string", "null"]
    target = ["string", None, None, "string", None]
    cells, notes = schema.read_cells(source)
    assert cells == target
    assert len(notes) == 5


def test_schema_read_cells_too_short():
    schema = Schema.from_descriptor(DESCRIPTOR_MAX)
    source = ["string", "10.0", "1", "string"]
    target = ["string", Decimal(10.0), 1, "string", None]
    cells, notes = schema.read_cells(source)
    assert cells == target
    assert len(notes) == 5


def test_schema_read_cells_too_long():
    schema = Schema.from_descriptor(DESCRIPTOR_MAX)
    source = ["string", "10.0", "1", "string", "string", "string"]
    target = ["string", Decimal(10.0), 1, "string", "string"]
    cells, notes = schema.read_cells(source)
    assert cells == target
    assert len(notes) == 5


def test_schema_read_cells_wrong_type():
    schema = Schema.from_descriptor(DESCRIPTOR_MAX)
    source = ["string", "notdecimal", "10.6", "string", "string"]
    target = ["string", None, None, "string", "string"]
    cells, notes = schema.read_cells(source)
    assert cells == target
    assert notes[1] == {"type": 'type is "number/default"'}
    assert notes[2] == {"type": 'type is "integer/default"'}


def test_schema_missing_values():
    assert Schema.from_descriptor(DESCRIPTOR_MIN).missing_values == [""]
    assert Schema.from_descriptor(DESCRIPTOR_MAX).missing_values == ["", "-", "null"]


def test_schema_fields():
    expect = ["id", "height"]
    actual = [field.name for field in Schema.from_descriptor(DESCRIPTOR_MIN).fields]
    assert expect == actual


def test_schema_get_field():
    schema = Schema.from_descriptor(DESCRIPTOR_MIN)
    assert schema.get_field("id").name == "id"
    assert schema.get_field("height").name == "height"


def test_schema_get_field_error_not_found():
    schema = Schema.from_descriptor(DESCRIPTOR_MIN)
    with pytest.raises(FrictionlessException) as excinfo:
        schema.get_field("bad")
    error = excinfo.value.error
    assert error.type == "schema-error"
    assert error.note == 'field "bad" does not exist'


def test_schema_update_field():
    schema = Schema.from_descriptor(DESCRIPTOR_MIN)
    schema.set_field_type("id", "number")
    schema.set_field_type("height", "number")
    assert schema.get_field("id").type == "number"
    assert schema.get_field("height").type == "number"


def test_schema_has_field():
    schema = Schema.from_descriptor(DESCRIPTOR_MIN)
    assert schema.has_field("id")
    assert schema.has_field("height")
    assert not schema.has_field("undefined")


def test_schema_remove_field():
    schema = Schema.from_descriptor(DESCRIPTOR_MIN)
    assert schema.remove_field("height")
    assert schema.field_names == ["id"]


def test_schema_remove_field_error_not_found():
    schema = Schema.from_descriptor(DESCRIPTOR_MIN)
    with pytest.raises(FrictionlessException) as excinfo:
        schema.remove_field("bad")
    error = excinfo.value.error
    assert error.type == "schema-error"
    assert error.note == 'field "bad" does not exist'


def test_schema_field_names():
    assert Schema.from_descriptor(DESCRIPTOR_MIN).field_names == ["id", "height"]


def test_schema_primary_key():
    assert Schema.from_descriptor(DESCRIPTOR_MIN).primary_key == []
    assert Schema.from_descriptor(DESCRIPTOR_MAX).primary_key == ["id"]


def test_schema_foreign_keys():
    assert Schema.from_descriptor(DESCRIPTOR_MIN).foreign_keys == []
    assert (
        Schema.from_descriptor(DESCRIPTOR_MAX).foreign_keys
        == DESCRIPTOR_MAX["foreignKeys"]
    )


def test_schema_add_then_remove_field():
    schema = Schema()
    schema.add_field(Field.from_descriptor({"name": "name", "type": "string"}))
    field = schema.remove_field("name")
    assert field.name == "name"


def test_schema_primary_foreign_keys_as_array():
    descriptor = {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "parent_id", "type": "string"},
        ],
        "primaryKey": ["name"],
        "foreignKeys": [
            {
                "fields": ["parent_id"],
                "reference": {"resource": "resource", "fields": ["id"]},
            }
        ],
    }
    schema = Schema.from_descriptor(descriptor)
    assert schema.primary_key == ["name"]
    assert schema.foreign_keys == [
        {"fields": ["parent_id"], "reference": {"resource": "resource", "fields": ["id"]}}
    ]


def test_schema_primary_foreign_keys_as_string():
    descriptor = {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "parent_id", "type": "string"},
        ],
        "primaryKey": "name",
        "foreignKeys": [
            {"fields": "parent_id", "reference": {"resource": "resource", "fields": "id"}}
        ],
    }
    schema = Schema.from_descriptor(descriptor)
    assert schema.primary_key == ["name"]
    assert schema.foreign_keys == [
        {"fields": ["parent_id"], "reference": {"resource": "resource", "fields": ["id"]}}
    ]


@pytest.mark.parametrize(
    "source",
    [
        "data/schema-valid-simple.json",
        "data/schema-valid-full.json",
        "data/schema-valid-pk-array.json",
        "data/schema-valid-fk-array.json",
    ],
)
def test_schema_metadata_valid(source):
    assert Schema.from_descriptor(source)


@pytest.mark.parametrize(
    "source",
    [
        "data/schema-invalid-empty.json",
        "data/schema-invalid-pk-string.json",
        "data/schema-invalid-pk-array.json",
        "data/schema-invalid-fk-string.json",
        "data/schema-invalid-fk-no-reference.json",
        "data/schema-invalid-fk-array.json",
        "data/schema-invalid-fk-string-array-ref.json",
        "data/schema-invalid-fk-array-string-ref.json",
    ],
)
def test_schema_metadata_not_valid(source):
    with pytest.raises(FrictionlessException) as excinfo:
        Schema.from_descriptor(source)
    error = excinfo.value.error
    assert error.type == "schema-error"
    assert error.note == "descriptor is not valid"


@pytest.mark.skip(reason="issue-1222")
def test_schema_metadata_not_valid_multiple_errors():
    schema = Schema.from_descriptor("data/schema-invalid-multiple-errors.json")
    assert len(schema.list_metadata_errors()) == 5  # type: ignore


@pytest.mark.skip(reason="issue-1222")
def test_schema_metadata_not_valid_multiple_errors_with_pk():
    with pytest.raises(FrictionlessException) as excinfo:
        Schema.from_descriptor("data/schema-invalid-pk-is-wrong-type.json")
    reasons = excinfo.value.reasons
    assert len(reasons) == 3


def test_schema_metadata_error_message():
    with pytest.raises(FrictionlessException) as excinfo:
        Schema.from_descriptor({"fields": [{"name": "name", "type": "other"}]})
    error = excinfo.value.error
    assert error.type == "field-error"
    assert error.note == 'field type "other" is not supported'


def test_schema_metadata_error_bad_schema_format():
    with pytest.raises(FrictionlessException) as excinfo:
        Schema.from_descriptor(
            {
                "fields": [
                    {
                        "name": "name",
                        "type": "boolean",
                        "format": {"trueValues": "Yes", "falseValues": "No"},
                    }
                ]
            }
        )
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert error.type == "schema-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "field-error"
    assert reasons[0].note.count("is not of type 'string' at property 'format'")


def test_schema_valid_examples():
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "name", "type": "string", "example": "John"},
                {"name": "age", "type": "integer", "example": 42},
            ]
        }
    )
    assert schema.get_field("name").example == "John"


def test_schema_invalid_example():
    with pytest.raises(FrictionlessException) as excinfo:
        Schema.from_descriptor(
            {
                "fields": [
                    {
                        "name": "name",
                        "type": "number",
                        "example": "bad",
                    }
                ]
            }
        )
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert error.type == "schema-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "field-error"
    assert reasons[0].note == 'example value "bad" for field "name" is not valid'


@pytest.mark.parametrize("create_descriptor", [(False,), (True,)])
def test_schema_standard_specs_properties(create_descriptor):
    helpers = import_module("frictionless.helpers")
    options = dict(
        fields=[],
        missing_values=[],
        primary_key=[],
        foreign_keys=[],
    )
    schema = (
        Schema(**options)
        if not create_descriptor
        else Schema.from_descriptor(helpers.create_descriptor(**options))
    )
    assert schema.fields == []
    assert schema.missing_values == []
    assert schema.primary_key == []
    assert schema.foreign_keys == []


def test_schema_pprint():
    descriptor = {
        "fields": [
            {"name": "test_1", "type": "string", "format": "default"},
            {"name": "test_2", "type": "string", "format": "default"},
            {"name": "test_3", "type": "string", "format": "default"},
        ]
    }
    schema = Schema.from_descriptor(descriptor)
    expected = """
    {'fields': [{'name': 'test_1', 'type': 'string', 'format': 'default'},
                {'name': 'test_2', 'type': 'string', 'format': 'default'},
                {'name': 'test_3', 'type': 'string', 'format': 'default'}]}
    """
    print(repr(schema))
    assert repr(schema) == textwrap.dedent(expected).strip()


def test_schema_pprint_with_constraints():
    schema = Schema.from_descriptor("data/schema-valid.json")
    expected = """
    {'fields': [{'name': 'id',
                 'type': 'integer',
                 'title': 'ID',
                 'description': 'The id.',
                 'constraints': {'required': True}},
                {'name': 'name',
                 'type': 'string',
                 'title': 'Name',
                 'description': 'The name.',
                 'constraints': {'required': True}},
                {'name': 'age',
                 'type': 'integer',
                 'title': 'Age',
                 'description': 'The age.',
                 'constraints': {'required': True}}],
     'primaryKey': ['id']}
    """
    print(repr(schema))
    assert repr(schema) == textwrap.dedent(expected).strip()


# Bugs


def test_schema_field_date_format_issue_177():
    descriptor = {"fields": [{"name": "myfield", "type": "date", "format": "%d/%m/%y"}]}
    schema = Schema.from_descriptor(descriptor)
    assert schema


def test_schema_field_time_format_issue_177():
    descriptor = {"fields": [{"name": "myfield", "type": "time", "format": "%H:%M:%S"}]}
    schema = Schema.from_descriptor(descriptor)
    assert schema


def test_schema_add_remove_field_issue_218():
    descriptor = {
        "fields": [
            {"name": "test_1", "type": "string", "format": "default"},
            {"name": "test_2", "type": "string", "format": "default"},
            {"name": "test_3", "type": "string", "format": "default"},
        ]
    }
    test_schema = Schema.from_descriptor(descriptor)
    test_schema.remove_field("test_1")
    test_schema.add_field(
        Field.from_descriptor({"name": "test_4", "type": "string", "format": "default"})
    )


def test_schema_not_supported_type_issue_goodatbles_304():
    with pytest.raises(FrictionlessException) as excinfo:
        Schema.from_descriptor(
            {
                "fields": [
                    {"name": "name"},
                    {"name": "age", "type": "bad"},
                ]
            }
        )
    error = excinfo.value.error
    assert error.type == "field-error"
    assert error.note == 'field type "bad" is not supported'
