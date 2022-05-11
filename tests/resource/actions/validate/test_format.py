from frictionless import validate, helpers


IS_UNIX = not helpers.is_platform("windows")


def test_validate_format():
    report = validate("data/table.csv", format="csv")
    assert report.valid


def test_validate_format_non_tabular():
    report = validate("data/table.bad")
    assert report.valid
