from frictionless import validate


# Forbidden Value


def test_validate_forbidden_value():
    report = validate(
        "data/table.csv",
        extra_checks=[("forbidden-value", {"fieldName": "id", "forbidden": [2]})],
    )
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [3, 1, "forbidden-value"],
    ]


def test_validate_forbidden_value_task_error():
    report = validate(
        "data/table.csv",
        extra_checks=[("forbidden-value", {"fieldName": "bad", "forbidden": [2]})],
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
        extra_checks=[
            ("forbidden-value", {"fieldName": "row", "forbidden": [10]}),
            ("forbidden-value", {"fieldName": "name", "forbidden": ["mistake"]}),
            ("forbidden-value", {"fieldName": "row", "forbidden": [10]}),
            ("forbidden-value", {"fieldName": "name", "forbidden": ["error"]}),
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
        extra_checks=[
            ("forbidden-value", {"fieldName": "row", "forbidden": [10]}),
            (
                "forbidden-value",
                {"fieldName": "bad", "forbidden": ["mistake"]},
            ),
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
        extra_checks=[
            ("sequential-value", {"fieldName": "index2"}),
            ("sequential-value", {"fieldName": "index3"}),
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
        extra_checks=[
            ("sequential-value", {"fieldName": "row"}),
            ("sequential-value", {"fieldName": "bad"}),
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
        source,
        extra_checks=[("row-constraint", {"constraint": "salary == bonus * 5"})],
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
        extra_checks=[
            ("row-constraint", {"constraint": "vars()"}),
            ("row-constraint", {"constraint": "import(os)"}),
            ("row-constraint", {"constraint": "non_existent > 0"}),
        ],
    )
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [2, None, "row-constraint"],
        [2, None, "row-constraint"],
        [2, None, "row-constraint"],
    ]
