from frictionless import Resource, helpers


IS_UNIX = not helpers.is_platform("windows")


def test_validate_schema_invalid():
    source = [["name", "age"], ["Alex", "33"]]
    schema = {"fields": [{"name": "name"}, {"name": "age", "type": "bad"}]}
    resource = Resource(source, schema=schema)
    report = resource.validate()
    assert report.flatten(["code", "note"]) == [
        [
            "field-error",
            "\"{'name': 'age', 'type': 'bad'} is not valid under any of the given schemas\" at \"\" in metadata and at \"anyOf\" in profile",
        ],
    ]


def test_validate_schema_invalid_json():
    resource = Resource("data/table.csv", schema="data/invalid.json")
    report = resource.validate()
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, None, "schema-error"],
    ]


def test_validate_schema_extra_headers_and_cells():
    schema = {"fields": [{"name": "id", "type": "integer"}]}
    resource = Resource("data/table.csv", schema=schema)
    report = resource.validate()
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 2, "extra-label"],
        [2, 2, "extra-cell"],
        [3, 2, "extra-cell"],
    ]


def test_validate_schema_multiple_errors():
    source = "data/schema-errors.csv"
    schema = "data/schema-valid.json"
    resource = Resource(source, schema=schema)
    report = resource.validate(pick_errors=["#row"], limit_errors=3)
    assert report.task.partial
    assert report.task.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, 1, "type-error"],
        [4, 2, "constraint-error"],
        [4, 3, "constraint-error"],
    ]


def test_validate_schema_min_length_constraint():
    source = [["row", "word"], [2, "a"], [3, "ab"], [4, "abc"], [5, "abcd"], [6]]
    schema = {
        "fields": [
            {"name": "row", "type": "integer"},
            {"name": "word", "type": "string", "constraints": {"minLength": 2}},
        ]
    }
    resource = Resource(source, schema=schema)
    report = resource.validate(pick_errors=["constraint-error"])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [2, 2, "constraint-error"],
    ]


def test_validate_schema_max_length_constraint():
    source = [["row", "word"], [2, "a"], [3, "ab"], [4, "abc"], [5, "abcd"], [6]]
    schema = {
        "fields": [
            {"name": "row", "type": "integer"},
            {"name": "word", "type": "string", "constraints": {"maxLength": 2}},
        ]
    }
    resource = Resource(source, schema=schema)
    report = resource.validate(pick_errors=["constraint-error"])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, 2, "constraint-error"],
        [5, 2, "constraint-error"],
    ]


def test_validate_schema_minimum_constraint():
    source = [["row", "score"], [2, 1], [3, 2], [4, 3], [5, 4], [6]]
    schema = {
        "fields": [
            {"name": "row", "type": "integer"},
            {"name": "score", "type": "integer", "constraints": {"minimum": 2}},
        ]
    }
    resource = Resource(source, schema=schema)
    report = resource.validate(pick_errors=["constraint-error"])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [2, 2, "constraint-error"],
    ]


def test_validate_schema_maximum_constraint():
    source = [["row", "score"], [2, 1], [3, 2], [4, 3], [5, 4], [6]]
    schema = {
        "fields": [
            {"name": "row", "type": "integer"},
            {"name": "score", "type": "integer", "constraints": {"maximum": 2}},
        ]
    }
    resource = Resource(source, schema=schema)
    report = resource.validate(pick_errors=["constraint-error"])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, 2, "constraint-error"],
        [5, 2, "constraint-error"],
    ]


def test_validate_schema_foreign_key_error_self_referencing():
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


def test_validate_schema_foreign_key_error_self_referencing_invalid():
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
    assert report.flatten(["rowPosition", "fieldPosition", "code", "cells"]) == [
        [6, None, "foreign-key-error", ["5", "6", "Rome"]],
    ]


def test_validate_schema_unique_error():
    resource = Resource("data/unique-field.csv", schema="data/unique-field.json")
    report = resource.validate(pick_errors=["unique-error"])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [10, 1, "unique-error"],
    ]


def test_validate_schema_unique_error_and_type_error():
    source = [
        ["id", "unique_number"],
        ["a1", 100],
        ["a2", "bad"],
        ["a3", 100],
        ["a4", 0],
        ["a5", 0],
    ]
    schema = {
        "fields": [
            {"name": "id"},
            {"name": "unique_number", "type": "number", "constraints": {"unique": True}},
        ]
    }
    resource = Resource(source, schema=schema)
    report = resource.validate()
    assert report.flatten(["rowPosition", "fieldPosition", "code", "cells"]) == [
        [3, 2, "type-error", ["a2", "bad"]],
        [4, 2, "unique-error", ["a3", "100"]],
        [6, 2, "unique-error", ["a5", "0"]],
    ]


def test_validate_schema_primary_key_error():
    resource = Resource("data/unique-field.csv", schema="data/unique-field.json")
    report = resource.validate(pick_errors=["primary-key-error"])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [10, None, "primary-key-error"],
    ]


def test_validate_schema_primary_key_and_unique_error():
    resource = Resource(
        "data/unique-field.csv",
        schema="data/unique-field.json",
    )
    report = resource.validate()
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [10, 1, "unique-error"],
        [10, None, "primary-key-error"],
    ]


def test_validate_schema_primary_key_error_composite():
    source = [
        ["id", "name"],
        [1, "Alex"],
        [1, "John"],
        ["", "Paul"],
        [1, "John"],
        ["", None],
    ]
    schema = {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
        "primaryKey": ["id", "name"],
    }
    resource = Resource(source, schema=schema)
    report = resource.validate()
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [5, None, "primary-key-error"],
        [6, None, "blank-row"],
        [6, None, "primary-key-error"],
    ]
