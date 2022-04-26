from frictionless import validate, checks


# General


def test_validate_forbidden_value():
    report = validate(
        "data/table.csv",
        checks=[checks.forbidden_value(field_name="id", values=[2])],
    )
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [3, 1, "forbidden-value"],
    ]


def test_validate_forbidden_value_task_error():
    report = validate(
        "data/table.csv",
        checks=[{"code": "forbidden-value", "fieldName": "bad", "forbidden": [2]}],
    )
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
    report = validate(
        source,
        checks=[
            {"code": "forbidden-value", "fieldName": "row", "values": [10]},
            {"code": "forbidden-value", "fieldName": "name", "values": ["mistake"]},
            {"code": "forbidden-value", "fieldName": "row", "values": [10]},
            {"code": "forbidden-value", "fieldName": "name", "values": ["error"]},
        ],
    )
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, 2, "forbidden-value"],
        [5, 2, "forbidden-value"],
        [6, 2, "missing-cell"],
    ]


def test_validate_forbidden_value_many_rules_with_non_existent_field():
    source = [
        ["row", "name"],
        [2, "Alex"],
    ]
    report = validate(
        source,
        checks=[
            {"code": "forbidden-value", "fieldName": "row", "values": [10]},
            {"code": "forbidden-value", "fieldName": "bad", "values": ["mistake"]},
        ],
    )
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, None, "check-error"],
    ]
