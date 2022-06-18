from frictionless import Resource, Checklist


def test_resource_validate_bound_checklist():
    checklist = Checklist(pick_errors=["blank-label", "blank-row"])
    resource = Resource("data/invalid.csv", checklist=checklist)
    report = resource.validate()
    assert report.task.scope == ["blank-label", "blank-row"]
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 3, "blank-label"],
        [4, None, "blank-row"],
    ]