from frictionless import validate, checks


# General


def test_validate_duplicate_row():
    report = validate("data/duplicate-rows.csv", checks=[checks.duplicate_row()])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, None, "duplicate-row"],
    ]


def test_validate_duplicate_row_valid():
    report = validate("data/table.csv", checks=[{"code": "duplicate-row"}])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == []
