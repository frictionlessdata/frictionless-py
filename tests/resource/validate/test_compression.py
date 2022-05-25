from frictionless import Resource, helpers


IS_UNIX = not helpers.is_platform("windows")


def test_validate_compression():
    resource = Resource("data/table.csv.zip")
    report = resource.validate()
    assert report.valid


def test_validate_compression_explicit():
    resource = Resource("data/table.csv.zip", compression="zip")
    report = resource.validate()
    assert report.valid


def test_validate_compression_invalid():
    resource = Resource("data/table.csv.zip", compression="bad")
    report = resource.validate()
    assert report.flatten(["code", "note"]) == [
        ["compression-error", 'compression "bad" is not supported'],
    ]
