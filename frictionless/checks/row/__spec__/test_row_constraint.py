from frictionless import Checklist, Resource, checks

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
    resource = Resource(source)
    checklist = Checklist(checks=[checks.row_constraint(formula="salary == bonus * 5")])
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
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
    resource = Resource(source)
    checklist = Checklist.from_descriptor(
        {
            "checks": [
                {"type": "row-constraint", "formula": "vars()"},
                {"type": "row-constraint", "formula": "import(os)"},
                {"type": "row-constraint", "formula": "non_existent > 0"},
            ]
        }
    )
    report = resource.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [2, None, "row-constraint"],
        [2, None, "row-constraint"],
        [2, None, "row-constraint"],
    ]


def test_validate_row_constraint_list_in_formula_issue_817():
    source = [["val"], ["one"], ["two"]]
    resource = Resource(source)
    checklist = Checklist(
        checks=[
            checks.duplicate_row(),
            checks.row_constraint(formula="val in ['one', 'two']"),
        ],
    )
    report = resource.validate(checklist)
    assert report.valid
