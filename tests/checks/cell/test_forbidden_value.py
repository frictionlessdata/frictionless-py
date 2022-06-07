import pytest
from frictionless import Resource, Checklist, checks


# General


def test_validate_forbidden_value():
    resource = Resource("data/table.csv")
    report = resource.validate(
        checks=[
            checks.forbidden_value(field_name="id", values=[2]),
        ]
    )
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [3, 1, "forbidden-value"],
    ]


@pytest.mark.skip
def test_validate_forbidden_value_task_error():
    resource = Resource("data/table.csv")
    checklist = Checklist(
        {"checks": [{"code": "forbidden-value", "fieldName": "bad", "forbidden": [2]}]}
    )
    report = resource.validate(checklist)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, None, "task-error"],
    ]


def test_validate_forbidden_value_many_rules():
    source = [
        ["row", "name"],
        [2, "Alex"],
        [3, "John"],
        [4, "mistake"],
        [5, "error"],
        [6],
    ]
    resource = Resource(source)
    checklist = Checklist(
        {
            "checks": [
                {"code": "forbidden-value", "fieldName": "row", "values": [10]},
                {"code": "forbidden-value", "fieldName": "name", "values": ["mistake"]},
                {"code": "forbidden-value", "fieldName": "row", "values": [10]},
                {"code": "forbidden-value", "fieldName": "name", "values": ["error"]},
            ]
        }
    )
    report = resource.validate(checklist)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, 2, "forbidden-value"],
        [5, 2, "forbidden-value"],
        [6, 2, "missing-cell"],
    ]


@pytest.mark.skip
def test_validate_forbidden_value_many_rules_with_non_existent_field():
    source = [
        ["row", "name"],
        [2, "Alex"],
    ]
    resource = Resource(source)
    checklist = Checklist(
        {
            "checks": [
                {"code": "forbidden-value", "fieldName": "row", "values": [10]},
                {"code": "forbidden-value", "fieldName": "bad", "values": ["mistake"]},
            ]
        }
    )
    report = resource.validate(checklist)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, None, "check-error"],
    ]
