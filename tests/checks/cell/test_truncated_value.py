from frictionless import Resource, Checklist, checks


# General


def test_validate_truncated_values():
    source = [
        ["int", "str"],
        ["a" * 255, 32767],
        ["good", 2147483647],
    ]
    resource = Resource(source)
    report = resource.validate(checks=[checks.truncated_value()])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
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
    checklist = Checklist({"checks": [{"code": "truncated-value"}]})
    report = resource.validate(checklist)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == []
