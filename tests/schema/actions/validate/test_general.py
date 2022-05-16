from frictionless import Schema


# General


def test_validate():
    schema = Schema("data/schema.json")
    report = schema.validate()
    assert report.valid


def test_validate_invalid():
    schema = Schema({"fields": {}})
    report = schema.validate()
    assert report.flatten(["code", "note"]) == [
        [
            "schema-error",
            '"{} is not of type \'array\'" at "fields" in metadata and at "properties/fields/type" in profile',
        ],
    ]
