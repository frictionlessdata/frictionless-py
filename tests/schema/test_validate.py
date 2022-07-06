import pytest
from frictionless import Schema


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
