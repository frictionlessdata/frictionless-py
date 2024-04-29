from frictionless import Schema

# General


def test_validate():
    report = Schema.validate_descriptor("data/schema.json")
    assert report.valid


def test_validate_invalid():
    report = Schema.validate_descriptor({"fields": "bad"})
    assert report.flatten(["type", "note"]) == [
        [
            "schema-error",
            "'bad' is not of type 'array' at property 'fields'",
        ],
    ]


def test_validate_required_invalid():
    report = Schema.validate_descriptor("data/schema-invalid.json")
    assert report.flatten(["type", "note"]) == [
        [
            "field-error",
            '"required" should be set as "constraints.required"',
        ],
    ]


def test_validate_inline_set_default_field_type_if_missing():
    report = Schema.validate_descriptor(
        {"fields": [{"name": "name"}, {"name": "id", "type": "integer"}]}
    )
    assert report.flatten(["type", "note"]) == []


def test_validate_file_set_default_field_type_if_missing():
    report = Schema.validate_descriptor("data/invalid-schema.json")
    assert report.flatten(["type", "note"]) == []
