from frictionless import Resource, helpers


IS_UNIX = not helpers.is_platform("windows")


def test_validate_dialect_delimiter():
    resource = Resource("data/delimiter.csv", dialect={"delimiter": ";"})
    report = resource.validate()
    assert report.valid
    assert report.task.resource.stats["rows"] == 2
