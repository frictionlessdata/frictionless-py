from frictionless import validate


# General


def test_validate():
    report = validate("data/schema.json")
    assert report.valid


def test_validate_invalid():
    report = validate({"fields": {}})
    assert report.flatten(["code", "note"]) == [
        [
            "schema-error",
            '"{} is not of type \'array\'" at "fields" in metadata and at "properties/fields/type" in profile',
        ],
    ]
