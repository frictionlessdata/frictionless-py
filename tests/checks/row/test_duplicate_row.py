from frictionless import Resource, Checklist, checks


# General


def test_validate_duplicate_row():
    resource = Resource("data/duplicate-rows.csv")
    checklist = Checklist(checks=[checks.duplicate_row()])
    report = resource.validate(checklist)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, None, "duplicate-row"],
    ]


def test_validate_duplicate_row_valid():
    resource = Resource("data/table.csv")
    checklist = Checklist({"checks": [{"code": "duplicate-row"}]})
    report = resource.validate(checklist)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == []
