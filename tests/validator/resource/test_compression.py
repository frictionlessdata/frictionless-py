from frictionless.resources import TableResource

# General


def test_resource_validate_compression():
    resource = TableResource(path="data/table.csv.zip")
    report = resource.validate()
    assert report.valid


def test_resource_validate_compression_explicit():
    resource = TableResource(path="data/table.csv.zip", compression="zip")
    report = resource.validate()
    assert report.valid


def test_resource_validate_compression_invalid():
    resource = TableResource(path="data/table.csv.zip", compression="bad")
    report = resource.validate()
    assert report.flatten(["type", "note"]) == [
        ["compression-error", 'compression "bad" is not supported'],
    ]
