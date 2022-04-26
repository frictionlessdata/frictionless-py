from frictionless import validate, checks


# General


def test_validate_table_dimensions_num_rows():
    report = validate(
        "data/table-limits.csv",
        checks=[checks.table_dimensions(num_rows=42)],
    )
    assert report.flatten(["limits", "code"]) == [
        [{"requiredNumRows": 42, "numberRows": 3}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_num_rows_declarative():
    report = validate(
        "data/table-limits.csv",
        checks=[{"code": "table-dimensions", "numRows": 42}],
    )
    assert report.flatten(["limits", "code"]) == [
        [{"requiredNumRows": 42, "numberRows": 3}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_min_rows():
    report = validate(
        "data/table-limits.csv",
        checks=[checks.table_dimensions(min_rows=42)],
    )
    assert report.flatten(["limits", "code"]) == [
        [{"minRows": 42, "numberRows": 3}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_min_rows_declarative():
    report = validate(
        "data/table-limits.csv",
        checks=[{"code": "table-dimensions", "minRows": 42}],
    )
    assert report.flatten(["limits", "code"]) == [
        [{"minRows": 42, "numberRows": 3}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_max_rows():
    report = validate(
        "data/table-limits.csv",
        checks=[checks.table_dimensions(max_rows=2)],
    )
    assert report.flatten(["limits", "code"]) == [
        [{"maxRows": 2, "numberRows": 3}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_max_rows_declarative():
    report = validate(
        "data/table-limits.csv",
        checks=[{"code": "table-dimensions", "maxRows": 2}],
    )
    assert report.flatten(["limits", "code"]) == [
        [{"maxRows": 2, "numberRows": 3}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_num_fields():
    report = validate(
        "data/table-limits.csv",
        checks=[checks.table_dimensions(num_fields=42)],
    )
    assert report.flatten(["limits", "code"]) == [
        [{"requiredNumFields": 42, "numberFields": 4}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_num_fields_declarative():
    report = validate(
        "data/table-limits.csv", checks=[{"code": "table-dimensions", "numFields": 42}]
    )

    assert report.flatten(["limits", "code"]) == [
        [{"requiredNumFields": 42, "numberFields": 4}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_min_fields():
    report = validate(
        "data/table-limits.csv",
        checks=[checks.table_dimensions(min_fields=42)],
    )
    assert report.flatten(["limits", "code"]) == [
        [{"minFields": 42, "numberFields": 4}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_min_fields_declarative():
    report = validate(
        "data/table-limits.csv",
        checks=[{"code": "table-dimensions", "minFields": 42}],
    )
    assert report.flatten(["limits", "code"]) == [
        [{"minFields": 42, "numberFields": 4}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_max_fields():
    report = validate(
        "data/table-limits.csv",
        checks=[checks.table_dimensions(max_fields=2)],
    )
    assert report.flatten(["limits", "code"]) == [
        [{"maxFields": 2, "numberFields": 4}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_max_fields_declarative():
    report = validate(
        "data/table-limits.csv",
        checks=[{"code": "table-dimensions", "maxFields": 2}],
    )
    assert report.flatten(["limits", "code"]) == [
        [{"maxFields": 2, "numberFields": 4}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_no_limits():
    report = validate(
        "data/table-limits.csv",
        checks=[checks.table_dimensions()],
    )
    assert report.flatten(["limits", "code"]) == []


def test_validate_table_dimensions_no_limits_declarative():
    report = validate(
        "data/table-limits.csv",
        checks=[{"code": "table-dimensions"}],
    )
    assert report.flatten(["limits", "code"]) == []


def test_validate_table_dimensions_num_fields_num_rows_wrong():
    report = validate(
        "data/table-limits.csv",
        checks=[checks.table_dimensions(num_fields=3, num_rows=2)],
    )
    assert report.flatten(["limits", "code"]) == [
        [{"requiredNumFields": 3, "numberFields": 4}, "table-dimensions-error"],
        [{"requiredNumRows": 2, "numberRows": 3}, "table-dimensions-error"],
    ]


def test_validate_table_dimensions_num_fields_num_rows_wrong_declarative():
    report = validate(
        "data/table-limits.csv",
        checks=[{"code": "table-dimensions", "numFields": 3, "numRows": 2}],
    )
    assert report.flatten(["limits", "code"]) == [
        [{"requiredNumFields": 3, "numberFields": 4}, "table-dimensions-error"],
        [{"requiredNumRows": 2, "numberRows": 3}, "table-dimensions-error"],
    ]


def test_validate_table_dimensions_num_fields_num_rows_correct():
    report = validate(
        "data/table-limits.csv",
        checks=[checks.table_dimensions(num_fields=4, num_rows=3)],
    )
    assert report.flatten(["limits", "code"]) == []


def test_validate_table_dimensions_num_fields_num_rows_correct_declarative():
    report = validate(
        "data/table-limits.csv",
        checks=[{"code": "table-dimensions", "numFields": 4, "numRows": 3}],
    )
    assert report.flatten(["limits", "code"]) == []


def test_validate_table_dimensions_min_fields_max_rows_wrong():
    report = validate(
        "data/table-limits.csv",
        checks=[checks.table_dimensions(min_fields=5, max_rows=2)],
    )
    assert report.flatten(["limits", "code"]) == [
        [{"minFields": 5, "numberFields": 4}, "table-dimensions-error"],
        [{"maxRows": 2, "numberRows": 3}, "table-dimensions-error"],
    ]


def test_validate_table_dimensions_min_fields_max_rows_wrong_declarative():
    report = validate(
        "data/table-limits.csv",
        checks=[{"code": "table-dimensions", "minFields": 5, "maxRows": 2}],
    )
    assert report.flatten(["limits", "code"]) == [
        [{"minFields": 5, "numberFields": 4}, "table-dimensions-error"],
        [{"maxRows": 2, "numberRows": 3}, "table-dimensions-error"],
    ]


def test_validate_table_dimensions_min_fields_max_rows_correct():
    report = validate(
        "data/table-limits.csv",
        checks=[checks.table_dimensions(min_fields=4, max_rows=3)],
    )
    assert report.flatten(["limits", "code"]) == []


def test_validate_table_dimensions_min_fields_max_rows_correct_declarative():
    report = validate(
        "data/table-limits.csv",
        checks=[{"code": "table-dimensions", "minFields": 4, "maxRows": 3}],
    )
    assert report.flatten(["limits", "code"]) == []
