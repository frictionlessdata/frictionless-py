from frictionless.resources import TableResource

# General


def test_resource_validate_scheme():
    resource = TableResource(path="data/table.csv", scheme="file")
    report = resource.validate()
    assert report.valid


def test_resource_validate_scheme_invalid():
    resource = TableResource(path="bad://data/table.csv")
    report = resource.validate()
    assert report.flatten(["type", "note"]) == [
        ["scheme-error", 'scheme "bad" is not supported'],
    ]
