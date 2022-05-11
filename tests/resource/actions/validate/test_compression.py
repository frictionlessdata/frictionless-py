from frictionless import validate, helpers


IS_UNIX = not helpers.is_platform("windows")


def test_validate_compression():
    report = validate("data/table.csv.zip")
    assert report.valid


def test_validate_compression_explicit():
    report = validate("data/table.csv.zip", compression="zip")
    assert report.valid


def test_validate_compression_invalid():
    report = validate("data/table.csv.zip", compression="bad")
    assert report.flatten(["code", "note"]) == [
        ["compression-error", 'compression "bad" is not supported'],
    ]
