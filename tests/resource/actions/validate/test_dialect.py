from frictionless import validate, helpers


IS_UNIX = not helpers.is_platform("windows")


def test_validate_dialect_delimiter():
    report = validate("data/delimiter.csv", dialect={"delimiter": ";"})
    assert report.valid
    assert report.task.resource.stats["rows"] == 2
