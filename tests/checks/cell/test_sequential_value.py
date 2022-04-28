from frictionless import validate, checks


# General


def test_validate_sequential_value():
    source = [
        ["row", "index2", "index3"],
        [2, 1, 1],
        [3, 2, 3],
        [4, 3, 5],
        [5, 5, 6],
        [6],
    ]
    report = validate(
        source,
        checks=[
            checks.sequential_value(field_name="index2"),
            checks.sequential_value(field_name="index3"),
        ],
    )
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [3, 3, "sequential-value"],
        [5, 2, "sequential-value"],
        [6, 2, "missing-cell"],
        [6, 3, "missing-cell"],
    ]


def test_validate_sequential_value_non_existent_field():
    source = [
        ["row", "name"],
        [2, "Alex"],
        [3, "Brad"],
    ]
    report = validate(
        source,
        checks=[
            {"code": "sequential-value", "fieldName": "row"},
            {"code": "sequential-value", "fieldName": "bad"},
        ],
    )
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, None, "check-error"],
    ]
