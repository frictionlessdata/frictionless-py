from frictionless import Resource, helpers


IS_UNIX = not helpers.is_platform("windows")


def test_validate_format():
    resource = Resource("data/table.csv", format="csv")
    report = resource.validate()
    assert report.valid


def test_validate_format_non_tabular():
    resource = Resource("data/table.bad")
    report = resource.validate()
    assert report.valid
