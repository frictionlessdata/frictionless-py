from frictionless import Checklist, Resource, checks

# General


def test_validate_table_dimensions_num_rows():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(num_rows=42)])
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == [
        ["table-dimensions", "number of rows is 3, the required is 42"]
    ]


def test_validate_table_dimensions_num_rows_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist.from_descriptor(
        {"checks": [{"type": "table-dimensions", "numRows": 42}]}
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == [
        ["table-dimensions", "number of rows is 3, the required is 42"]
    ]


def test_validate_table_dimensions_min_rows():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(min_rows=42)])
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == [
        ["table-dimensions", "number of rows is 3, the minimum is 42"]
    ]


def test_validate_table_dimensions_min_rows_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist.from_descriptor(
        {"checks": [{"type": "table-dimensions", "minRows": 42}]}
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == [
        ["table-dimensions", "number of rows is 3, the minimum is 42"]
    ]


def test_validate_table_dimensions_max_rows():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(max_rows=2)])
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == [
        ["table-dimensions", "number of rows is 3, the maximum is 2"],
    ]


def test_validate_table_dimensions_max_rows_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist.from_descriptor(
        {"checks": [{"type": "table-dimensions", "maxRows": 2}]}
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == [
        ["table-dimensions", "number of rows is 3, the maximum is 2"],
    ]


def test_validate_table_dimensions_num_fields():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(num_fields=42)])
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == [
        ["table-dimensions", "number of fields is 4, the required is 42"]
    ]


def test_validate_table_dimensions_num_fields_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist.from_descriptor(
        {"checks": [{"type": "table-dimensions", "numFields": 42}]}
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == [
        ["table-dimensions", "number of fields is 4, the required is 42"]
    ]


def test_validate_table_dimensions_min_fields():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(min_fields=42)])
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == [
        ["table-dimensions", "number of fields is 4, the minimum is 42"]
    ]


def test_validate_table_dimensions_min_fields_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist.from_descriptor(
        {"checks": [{"type": "table-dimensions", "minFields": 42}]}
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == [
        ["table-dimensions", "number of fields is 4, the minimum is 42"]
    ]


def test_validate_table_dimensions_max_fields():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(max_fields=2)])
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == [
        ["table-dimensions", "number of fields is 4, the maximum is 2"]
    ]


def test_validate_table_dimensions_max_fields_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist.from_descriptor(
        {"checks": [{"type": "table-dimensions", "maxFields": 2}]}
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == [
        ["table-dimensions", "number of fields is 4, the maximum is 2"]
    ]


def test_validate_table_dimensions_no_limits():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions()])
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == []


def test_validate_table_dimensions_no_limits_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist.from_descriptor({"checks": [{"type": "table-dimensions"}]})
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == []


def test_validate_table_dimensions_num_fields_num_rows_wrong():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(num_fields=3, num_rows=2)])
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == [
        ["table-dimensions", "number of fields is 4, the required is 3"],
        ["table-dimensions", "number of rows is 3, the required is 2"],
    ]


def test_validate_table_dimensions_num_fields_num_rows_wrong_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist.from_descriptor(
        {"checks": [{"type": "table-dimensions", "numFields": 3, "numRows": 2}]}
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == [
        ["table-dimensions", "number of fields is 4, the required is 3"],
        ["table-dimensions", "number of rows is 3, the required is 2"],
    ]


def test_validate_table_dimensions_num_fields_num_rows_correct():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(num_fields=4, num_rows=3)])
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == []


def test_validate_table_dimensions_num_fields_num_rows_correct_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist.from_descriptor(
        {"checks": [{"type": "table-dimensions", "numFields": 4, "numRows": 3}]}
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == []


def test_validate_table_dimensions_min_fields_max_rows_wrong():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(min_fields=5, max_rows=2)])
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == [
        ["table-dimensions", "number of fields is 4, the minimum is 5"],
        ["table-dimensions", "number of rows is 3, the maximum is 2"],
    ]


def test_validate_table_dimensions_min_fields_max_rows_wrong_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist.from_descriptor(
        {"checks": [{"type": "table-dimensions", "minFields": 5, "maxRows": 2}]}
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == [
        ["table-dimensions", "number of fields is 4, the minimum is 5"],
        ["table-dimensions", "number of rows is 3, the maximum is 2"],
    ]


def test_validate_table_dimensions_min_fields_max_rows_correct():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist(checks=[checks.table_dimensions(min_fields=4, max_rows=4)])
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == []


def test_validate_table_dimensions_min_fields_max_rows_correct_declarative():
    resource = Resource("data/table-limits.csv")
    checklist = Checklist.from_descriptor(
        {"checks": [{"type": "table-dimensions", "minFields": 4, "maxRows": 4}]}
    )
    report = resource.validate(checklist)
    assert report.flatten(["type", "note"]) == []
