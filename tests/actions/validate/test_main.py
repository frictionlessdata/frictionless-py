from frictionless import Schema, validate, fields


# Table


def test_validate():
    report = validate("data/table.csv")
    assert report.valid


def test_validate_invalid():
    report = validate("data/invalid.csv")
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 3, "blank-label"],
        [None, 4, "duplicate-label"],
        [2, 3, "missing-cell"],
        [2, 4, "missing-cell"],
        [3, 3, "missing-cell"],
        [3, 4, "missing-cell"],
        [4, None, "blank-row"],
        [5, 5, "extra-cell"],
    ]


# Bugs


def test_validate_multiple_files_issue_850():
    report = validate("data/package/*.csv")
    assert report.stats.tasks == 2


def test_validate_less_actual_fields_with_required_constraint_issue_950():
    schema = Schema.describe("data/table.csv")
    schema.add_field(fields.AnyField(name="bad", constraints={"required": True}))
    report = validate("data/table.csv", schema=schema)
    print(report.flatten(["rowNumber", "fieldNumber", "type"]))
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 3, "missing-label"],
        [2, 3, "constraint-error"],
        [2, 3, "missing-cell"],
        [3, 3, "constraint-error"],
        [3, 3, "missing-cell"],
    ]
