from frictionless.resources import TableResource

# General


def test_resource_validate_format():
    resource = TableResource(path="data/table.csv", format="csv")
    report = resource.validate()
    assert report.valid
