from frictionless import Checklist, Resource, checks

# General


def test_validate_truncated_values():
    source = [
        ["int", "str"],
        ["a" * 255, 32767],
        ["good", 2147483647],
    ]
    resource = Resource(source)
    checklist = Checklist(checks=[checks.truncated_value()])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [2, 1, "truncated-value"],
        [2, 2, "truncated-value"],
        [3, 2, "truncated-value"],
    ]


def test_validate_truncated_values_close_to_errors():
    source = [
        ["int", "str"],
        ["a" * 254, 32766],
        ["good", 2147483646],
    ]
    resource = Resource(source)
    checklist = Checklist.from_descriptor({"checks": [{"type": "truncated-value"}]})
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == []
