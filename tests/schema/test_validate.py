import pytest
from frictionless import Schema, FrictionlessException


# General


def test_validate():
    schema = Schema.from_descriptor("data/schema.json")
    report = schema.validate()
    assert report.valid


def test_validate_invalid():
    with pytest.raises(FrictionlessException) as excinfo:
        Schema.from_descriptor({"fields": "bad"})
    error = excinfo.value.error
    assert error.type == "schema-error"
    assert error.note == '"fields" is required to be an array'


def test_validate_required_invalid():
    schema = Schema.from_descriptor("data/schema-invalid.json")
    report = schema.validate()
    assert report.flatten(["type", "note"]) == [
        [
            "field-error",
            '"required" should be set as "constraints.required"',
        ],
    ]
