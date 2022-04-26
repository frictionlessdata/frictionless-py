from frictionless import validate, checks


# General


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


def test_validate_row_constraint_list_in_formula_issue_817():
    data = [["val"], ["one"], ["two"]]
    report = validate(
        data,
        checks=[
            checks.duplicate_row(),
            checks.row_constraint(formula="val in ['one', 'two']"),
        ],
    )
    assert report.valid
