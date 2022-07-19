import pytest
from frictionless import Schema
from frictionless import FrictionlessException


# General


def test_validate():
    schema = Schema.from_descriptor("data/schema.json")
    report = schema.validate()
    assert report.valid


@pytest.mark.xfail(reason="Not yet decided how to handle these situations")
def test_validate_invalid():
    schema = Schema.from_descriptor({"fields": "bad"})
    report = schema.validate()
    assert report.flatten(["code", "note"]) == [
        [
            "schema-error",
            '"{} is not of type \'array\'" at "fields" in metadata and at "properties/fields/type" in profile',
        ],
    ]


def test_validate_required_invalid():
    schema = Schema.from_descriptor("data/schema-invalid.json")
    with pytest.raises(FrictionlessException) as exception:
        schema.validate()
    error = exception.value.error
    assert error.type == "field-error"
    assert error.note == 'required should be part of "field->constraints" not field.'
