from frictionless import validate, checks


# Forbidden Value


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
        [None, None, "task-error"],
    ]


# Sequential Value


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
        [None, None, "task-error"],
    ]


# Row constraint


def test_validate_row_constraint():
    source = [
        ["row", "salary", "bonus"],
        [2, 1000, 200],
        [3, 2500, 500],
        [4, 1300, 500],
        [5, 5000, 1000],
        [6],
    ]
    report = validate(
        source, checks=[checks.row_constraint(formula="salary == bonus * 5")]
    )
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, None, "row-constraint"],
        [6, 2, "missing-cell"],
        [6, 3, "missing-cell"],
        [6, None, "row-constraint"],
    ]


def test_validate_row_constraint_incorrect_constraint():
    source = [
        ["row", "name"],
        [2, "Alex"],
    ]
    report = validate(
        source,
        checks=[
            {"code": "row-constraint", "formula": "vars()"},
            {"code": "row-constraint", "formula": "import(os)"},
            {"code": "row-constraint", "formula": "non_existent > 0"},
        ],
    )
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [2, None, "row-constraint"],
        [2, None, "row-constraint"],
        [2, None, "row-constraint"],
    ]
