import json
import yaml
import pytest
from frictionless import Schema, FrictionlessException


UNZIPPED_DIR = "data/fixtures/output-unzipped"
DESCRIPTOR = {
    "fields": [
        {
            "name": "id",
            "description": "Any positive integer",
            "type": "integer",
            "constraints": {"minimum": 1},
        },
        {
            "name": "age",
            "title": "Age",
            "description": "Any number >= 1",
            "type": "number",
            "constraints": {"minimum": 1},
        },
    ]
}
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
    "primaryKey": ["id"],
    "foreignKeys": [
        {"fields": ["name"], "reference": {"resource": "", "fields": ["id"]}}
    ],
    "missingValues": ["", "-", "null"],
}


# General


def test_schema_to_copy():
    source = Schema.describe("data/table.csv")
    target = source.to_copy()
    assert source is not target
    assert source.to_descriptor() == target.to_descriptor()


def test_schema_to_json(tmpdir):
    output_file_path = str(tmpdir.join("schema.json"))
    schema = Schema.from_descriptor(DESCRIPTOR_MIN)
    schema.to_json(output_file_path)
    with open(output_file_path, encoding="utf-8") as file:
        assert schema.to_descriptor() == json.load(file)


def test_schema_to_yaml(tmpdir):
    output_file_path = str(tmpdir.join("schema.yaml"))
    schema = Schema.from_descriptor(DESCRIPTOR_MIN)
    schema.to_yaml(output_file_path)
    with open(output_file_path, encoding="utf-8") as file:
        assert schema.to_descriptor() == yaml.safe_load(file)


# Summary


def test_schema_to_summary():
    schema = Schema.from_descriptor(DESCRIPTOR_MAX)
    output = schema.to_summary()
    assert (
        output.count("| name       | type    | required   |")
        and output.count("| id         | string  | True       |")
        and output.count("| height     | number  |            |")
        and output.count("| age        | integer |            |")
        and output.count("| name       | string  |            |")
    )


def test_schema_to_summary_without_required():
    descriptor = {
        "fields": [
            {"name": "test_1", "type": "string", "format": "default"},
            {"name": "test_2", "type": "string", "format": "default"},
            {"name": "test_3", "type": "string", "format": "default"},
        ]
    }
    schema = Schema.from_descriptor(descriptor)
    output = schema.to_summary()
    assert (
        output.count("| name   | type   | required   |")
        and output.count("| test_1 | string |            |")
        and output.count("| test_2 | string |            |")
        and output.count("| test_3 | string |            |")
    )


def test_schema_to_summary_with_type_missing_for_some_fields():
    descriptor = {
        "fields": [
            {"name": "id", "format": "default"},
            {"name": "name", "type": "string", "format": "default"},
            {"name": "age", "format": "default"},
        ]
    }
    with pytest.raises(FrictionlessException) as excinfo:
        Schema.from_descriptor(descriptor)
    error = excinfo.value.error
    assert error.type == "schema-error"
    assert error.description == "Provided schema is not valid."


def test_schema_to_summary_with_name_missing_for_some_fields():
    descriptor = {
        "fields": [
            {"type": "integer", "format": "default"},
            {"type": "integer", "format": "default"},
            {"name": "name", "type": "string", "format": "default"},
        ]
    }
    with pytest.raises(FrictionlessException) as excinfo:
        Schema.from_descriptor(descriptor)
    error = excinfo.value.error
    assert error.type == "schema-error"
    assert error.description == "Provided schema is not valid."
