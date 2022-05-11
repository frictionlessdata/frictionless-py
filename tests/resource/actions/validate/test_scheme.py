from frictionless import validate, helpers


IS_UNIX = not helpers.is_platform("windows")


def test_validate_scheme():
    report = validate("data/table.csv", scheme="file")
    assert report.valid


def test_validate_scheme_invalid():
    report = validate("bad://data/table.csv")
    assert report.flatten(["code", "note"]) == [
        ["scheme-error", 'cannot create loader "bad". Try installing "frictionless-bad"'],
    ]
