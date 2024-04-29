from frictionless import Checklist, Resource, checks

# General


def test_validate_forbidden_value():
    resource = Resource("data/table.csv")
    checklist = Checklist(
        checks=[
            checks.forbidden_value(field_name="id", values=[2]),
        ]
    )
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [3, 1, "forbidden-value"],
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
    checklist = Checklist.from_descriptor(
        {
            "checks": [
                {"type": "forbidden-value", "fieldName": "row", "values": [10]},
                {"type": "forbidden-value", "fieldName": "name", "values": ["mistake"]},
                {"type": "forbidden-value", "fieldName": "row", "values": [10]},
                {"type": "forbidden-value", "fieldName": "name", "values": ["error"]},
            ]
        }
    )
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [4, 2, "forbidden-value"],
        [5, 2, "forbidden-value"],
        [6, 2, "missing-cell"],
    ]


def test_validate_forbidden_value_many_rules_with_non_existent_field():
    source = [
        ["row", "name"],
        [2, "Alex"],
    ]
    resource = Resource(source)
    checklist = Checklist.from_descriptor(
        {
            "checks": [
                {"type": "forbidden-value", "fieldName": "row", "values": [10]},
                {"type": "forbidden-value", "fieldName": "bad", "values": ["mistake"]},
            ]
        }
    )
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, None, "check-error"],
    ]
