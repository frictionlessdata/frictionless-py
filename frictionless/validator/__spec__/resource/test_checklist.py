from frictionless import Checklist
from frictionless.resources import TableResource

# General


def test_resource_validate_bound_checklist():
    checklist = Checklist(pick_errors=["blank-label", "blank-row"])
    resource = TableResource(path="data/invalid.csv")
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 3, "blank-label"],
        [4, None, "blank-row"],
    ]
