from frictionless import Resource


# General


def test_resource_validate_format():
    resource = Resource("data/table.csv", format="csv")
    report = resource.validate()
    assert report.valid


def test_resource_validate_format_non_tabular():
    resource = Resource("data/table.bad")
    report = resource.validate()
    assert report.valid
