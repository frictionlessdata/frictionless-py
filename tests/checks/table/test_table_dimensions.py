from frictionless import Resource, Checklist, checks


# General


def test_validate_table_dimensions_num_rows():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(num_rows=42)])
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == [
        [{"requiredNumRows": 42, "numberRows": 3}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_num_rows_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist({"checks": [{"code": "table-dimensions", "numRows": 42}]})
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == [
        [{"requiredNumRows": 42, "numberRows": 3}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_min_rows():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(min_rows=42)])
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == [
        [{"minRows": 42, "numberRows": 3}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_min_rows_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist({"checks": [{"code": "table-dimensions", "minRows": 42}]})
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == [
        [{"minRows": 42, "numberRows": 3}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_max_rows():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(max_rows=2)])
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == [
        [{"maxRows": 2, "numberRows": 3}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_max_rows_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist({"checks": [{"code": "table-dimensions", "maxRows": 2}]})
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == [
        [{"maxRows": 2, "numberRows": 3}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_num_fields():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(num_fields=42)])
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == [
        [{"requiredNumFields": 42, "numberFields": 4}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_num_fields_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist({"checks": [{"code": "table-dimensions", "numFields": 42}]})
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == [
        [{"requiredNumFields": 42, "numberFields": 4}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_min_fields():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(min_fields=42)])
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == [
        [{"minFields": 42, "numberFields": 4}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_min_fields_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist({"checks": [{"code": "table-dimensions", "minFields": 42}]})
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == [
        [{"minFields": 42, "numberFields": 4}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_max_fields():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(max_fields=2)])
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == [
        [{"maxFields": 2, "numberFields": 4}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_max_fields_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist({"checks": [{"code": "table-dimensions", "maxFields": 2}]})
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == [
        [{"maxFields": 2, "numberFields": 4}, "table-dimensions-error"]
    ]


def test_validate_table_dimensions_no_limits():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions()])
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == []


def test_validate_table_dimensions_no_limits_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist({"checks": [{"code": "table-dimensions"}]})
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == []


def test_validate_table_dimensions_num_fields_num_rows_wrong():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(num_fields=3, num_rows=2)])
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == [
        [{"requiredNumFields": 3, "numberFields": 4}, "table-dimensions-error"],
        [{"requiredNumRows": 2, "numberRows": 3}, "table-dimensions-error"],
    ]


def test_validate_table_dimensions_num_fields_num_rows_wrong_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(
        {"checks": [{"code": "table-dimensions", "numFields": 3, "numRows": 2}]}
    )
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == [
        [{"requiredNumFields": 3, "numberFields": 4}, "table-dimensions-error"],
        [{"requiredNumRows": 2, "numberRows": 3}, "table-dimensions-error"],
    ]


def test_validate_table_dimensions_num_fields_num_rows_correct():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(num_fields=4, num_rows=3)])
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == []


def test_validate_table_dimensions_num_fields_num_rows_correct_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(
        {"checks": [{"code": "table-dimensions", "numFields": 4, "numRows": 3}]}
    )
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == []


def test_validate_table_dimensions_min_fields_max_rows_wrong():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(min_fields=5, max_rows=2)])
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == [
        [{"minFields": 5, "numberFields": 4}, "table-dimensions-error"],
        [{"maxRows": 2, "numberRows": 3}, "table-dimensions-error"],
    ]


def test_validate_table_dimensions_min_fields_max_rows_wrong_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(
        {"checks": [{"code": "table-dimensions", "minFields": 5, "maxRows": 2}]}
    )
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == [
        [{"minFields": 5, "numberFields": 4}, "table-dimensions-error"],
        [{"maxRows": 2, "numberRows": 3}, "table-dimensions-error"],
    ]


def test_validate_table_dimensions_min_fields_max_rows_correct():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(min_fields=4, max_rows=3)])
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == []


def test_validate_table_dimensions_min_fields_max_rows_correct_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(
        {"checks": [{"code": "table-dimensions", "minFields": 4, "maxRows": 3}]}
    )
    report = resource.validate(checklist)
    assert report.flatten(["limits", "code"]) == []
