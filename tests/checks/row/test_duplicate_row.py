from frictionless import Checklist, Resource, checks

# General


def test_validate_duplicate_row():
    resource = Resource("data/duplicate-rows.csv")
    checklist = Checklist(checks=[checks.duplicate_row()])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [4, None, "duplicate-row"],
    ]


def test_validate_duplicate_row_valid():
    resource = Resource("data/table.csv")
    checklist = Checklist.from_descriptor({"checks": [{"type": "duplicate-row"}]})
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == []
