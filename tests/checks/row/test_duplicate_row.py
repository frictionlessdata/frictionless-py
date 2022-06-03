from frictionless import Resource, checks


# General


def test_validate_duplicate_row():
    resource = Resource("data/duplicate-rows.csv")
    report = resource.validate(checks=[checks.duplicate_row()])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, None, "duplicate-row"],
    ]


def test_validate_duplicate_row_valid():
    resource = Resource("data/table.csv")
    report = resource.validate(checks=[{"code": "duplicate-row"}])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == []
