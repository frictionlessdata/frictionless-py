import pytest
from frictionless import Schema2


# General


def test_validate():
    schema = Schema2.from_descriptor("data/schema.json")
    report = schema.validate()
    assert report.valid


@pytest.mark.skip
def test_validate_invalid():
    schema = Schema2.from_descriptor({"fields": {}})
    report = schema.validate()
    assert report.flatten(["code", "note"]) == [
        [
            "schema-error",
            '"{} is not of type \'array\'" at "fields" in metadata and at "properties/fields/type" in profile',
        ],
    ]
