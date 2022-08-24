import pytest
from frictionless import Resource, Schema, Checklist, Detector, FrictionlessException


# General


def test_resource_validate_schema_invalid_json():
    descriptor = dict(path="data/table.csv", schema="data/invalid.json")
    report = Resource.validate_descriptor(descriptor)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, None, "schema-error"],
    ]


def test_resource_validate_invalid_resource():
    report = Resource.validate_descriptor({"path": "data/table.csv", "schema": "bad"})
    assert report.stats.errors == 1
    [[type, note]] = report.flatten(["type", "note"])
    assert type == "schema-error"
    assert note.count("[Errno 2]") and note.count("bad")


def test_resource_validate_schema_extra_headers_and_cells():
    schema = Schema.from_descriptor({"fields": [{"name": "id", "type": "integer"}]})
    resource = Resource("data/table.csv", schema=schema)
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 2, "extra-label"],
        [2, 2, "extra-cell"],
        [3, 2, "extra-cell"],
    ]


def test_resource_validate_schema_multiple_errors():
    source = "data/schema-errors.csv"
    schema = "data/schema-valid.json"
    resource = Resource(source, schema=schema)
    checklist = Checklist(pick_errors=["#row"])
    report = resource.validate(checklist, limit_errors=3)
    assert report.task.warnings == ["reached error limit: 3"]
    assert report.task.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [4, 1, "type-error"],
        [4, 2, "constraint-error"],
        [4, 3, "constraint-error"],
    ]


def test_resource_validate_schema_min_length_constraint():
    source = [["row", "word"], [2, "a"], [3, "ab"], [4, "abc"], [5, "abcd"], [6]]
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "row", "type": "integer"},
                {"name": "word", "type": "string", "constraints": {"minLength": 2}},
            ]
        }
    )
    resource = Resource(source, schema=schema)
    checklist = Checklist(pick_errors=["constraint-error"])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [2, 2, "constraint-error"],
    ]


def test_resource_validate_schema_max_length_constraint():
    source = [["row", "word"], [2, "a"], [3, "ab"], [4, "abc"], [5, "abcd"], [6]]
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "row", "type": "integer"},
                {"name": "word", "type": "string", "constraints": {"maxLength": 2}},
            ]
        }
    )
    resource = Resource(source, schema=schema)
    checklist = Checklist(pick_errors=["constraint-error"])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [4, 2, "constraint-error"],
        [5, 2, "constraint-error"],
    ]


def test_resource_validate_schema_minimum_constraint():
    source = [["row", "score"], [2, 1], [3, 2], [4, 3], [5, 4], [6]]
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "row", "type": "integer"},
                {"name": "score", "type": "integer", "constraints": {"minimum": 2}},
            ]
        }
    )
    resource = Resource(source, schema=schema)
    checklist = Checklist(pick_errors=["constraint-error"])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [2, 2, "constraint-error"],
    ]


def test_resource_validate_schema_maximum_constraint():
    source = [["row", "score"], [2, 1], [3, 2], [4, 3], [5, 4], [6]]
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "row", "type": "integer"},
                {"name": "score", "type": "integer", "constraints": {"maximum": 2}},
            ]
        }
    )
    resource = Resource(source, schema=schema)
    checklist = Checklist(pick_errors=["constraint-error"])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [4, 2, "constraint-error"],
        [5, 2, "constraint-error"],
    ]


def test_resource_validate_schema_foreign_key_error_self_referencing():
    source = {
        "path": "data/nested.csv",
        "schema": {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "cat", "type": "integer"},
                {"name": "name", "type": "string"},
            ],
            "foreignKeys": [
                {"fields": "cat", "reference": {"resource": "", "fields": "id"}}
            ],
        },
    }
    resource = Resource(source)
    report = resource.validate()
    assert report.valid


def test_resource_validate_schema_foreign_key_error_self_referencing_invalid():
    source = {
        "path": "data/nested-invalid.csv",
        "schema": {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "cat", "type": "integer"},
                {"name": "name", "type": "string"},
            ],
            "foreignKeys": [
                {"fields": "cat", "reference": {"resource": "", "fields": "id"}}
            ],
        },
    }
    resource = Resource(source)
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells"]) == [
        [6, None, "foreign-key", ["5", "6", "Rome"]],
    ]


def test_resource_validate_schema_unique_error():
    resource = Resource("data/unique-field.csv", schema="data/unique-field.json")
    checklist = Checklist(pick_errors=["unique-error"])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [10, 1, "unique-error"],
    ]


def test_resource_validate_schema_unique_error_and_type_error():
    source = [
        ["id", "unique_number"],
        ["a1", 100],
        ["a2", "bad"],
        ["a3", 100],
        ["a4", 0],
        ["a5", 0],
    ]
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "id", "type": "string"},
                {
                    "name": "unique_number",
                    "type": "number",
                    "constraints": {"unique": True},
                },
            ]
        }
    )
    resource = Resource(source, schema=schema)
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type", "cells"]) == [
        [3, 2, "type-error", ["a2", "bad"]],
        [4, 2, "unique-error", ["a3", "100"]],
        [6, 2, "unique-error", ["a5", "0"]],
    ]


def test_resource_validate_schema_primary_key_error():
    resource = Resource("data/unique-field.csv", schema="data/unique-field.json")
    checklist = Checklist(pick_errors=["primary-key"])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [10, None, "primary-key"],
    ]


def test_resource_validate_schema_primary_key_and_unique_error():
    resource = Resource(
        "data/unique-field.csv",
        schema="data/unique-field.json",
    )
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [10, 1, "unique-error"],
        [10, None, "primary-key"],
    ]


def test_resource_validate_schema_primary_key_error_composite():
    source = [
        ["id", "name"],
        [1, "Alex"],
        [1, "John"],
        ["", "Paul"],
        [1, "John"],
        ["", None],
    ]
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ],
            "primaryKey": ["id", "name"],
        }
    )
    resource = Resource(source, schema=schema)
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [5, None, "primary-key"],
        [6, None, "blank-row"],
        [6, None, "primary-key"],
    ]


# Bugs


def test_resource_validate_invalid_table_schema_issue_304():
    descriptor = {
        "data": [["name", "age"], ["Alex", "33"]],
        "schema": {
            "fields": [
                {"name": "name", "type": "string"},
                {"name": "age", "type": "bad"},
            ]
        },
    }
    with pytest.raises(FrictionlessException) as excinfo:
        Resource(descriptor)
    error = excinfo.value.error
    # TODO: why it's not a descriptor error with exception.reasons?
    assert error.type == "field-error"
    assert error.note == 'field type "bad" is not supported'


def test_resource_validate_resource_duplicate_labels_with_sync_schema_issue_910():
    detector = Detector(schema_sync=True)
    resource = Resource(
        "data/duplicate-column.csv",
        schema="data/duplicate-column-schema.json",
        detector=detector,
    )
    report = resource.validate()
    assert report.flatten(["type", "note"]) == [
        ["error", '"schema_sync" requires unique labels in the header'],
    ]
