from frictionless import validate


# General


def test_validate():
    report = validate("data/schema.json")
    assert report.valid


def test_validate_invalid():
    report = validate({"fields": "bad"})
    assert report.flatten(["type", "note"]) == [
        ["schema-error", "'bad' is not of type 'array' at property 'fields'"],
    ]
