from frictionless import Layout, Resource, helpers


IS_UNIX = not helpers.is_platform("windows")


def test_validate_layout_none():
    layout = Layout(header=False)
    resource = Resource("data/without-headers.csv", layout=layout)
    report = resource.validate()
    assert report.valid
    assert report.task.resource.stats["rows"] == 3
    assert report.task.resource.layout.header is False
    assert report.task.resource.labels == []
    assert report.task.resource.header == ["field1", "field2"]


def test_validate_layout_none_extra_cell():
    layout = Layout(header=False)
    resource = Resource("data/without-headers-extra.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.stats["rows"] == 3
    assert report.task.resource.layout.header is False
    assert report.task.resource.labels == []
    assert report.task.resource.header == ["field1", "field2"]
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [3, 3, "extra-cell"],
    ]


def test_validate_layout_number():
    layout = Layout(header_rows=[2])
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["11", "12", "13", "14"]
    assert report.valid


def test_validate_layout_list_of_numbers():
    layout = Layout(header_rows=[2, 3, 4])
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["11 21 31", "12 22 32", "13 23 33", "14 24 34"]
    assert report.valid


def test_validate_layout_list_of_numbers_and_headers_join():
    layout = Layout(header_rows=[2, 3, 4], header_join=".")
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["11.21.31", "12.22.32", "13.23.33", "14.24.34"]
    assert report.valid


def test_validate_layout_pick_fields():
    layout = Layout(pick_fields=[2, "f3"])
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["f2", "f3"]
    assert report.task.resource.stats["rows"] == 4
    assert report.task.valid


def test_validate_layout_pick_fields_regex():
    layout = Layout(pick_fields=["<regex>f[23]"])
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["f2", "f3"]
    assert report.task.resource.stats["rows"] == 4
    assert report.task.valid


def test_validate_layout_skip_fields():
    layout = Layout(skip_fields=[1, "f4"])
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["f2", "f3"]
    assert report.task.resource.stats["rows"] == 4
    assert report.task.valid


def test_validate_layout_skip_fields_regex():
    layout = Layout(skip_fields=["<regex>f[14]"])
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["f2", "f3"]
    assert report.task.resource.stats["rows"] == 4
    assert report.task.valid


def test_validate_layout_limit_fields():
    layout = Layout(limit_fields=1)
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["f1"]
    assert report.task.resource.stats["rows"] == 4
    assert report.task.valid


def test_validate_layout_offset_fields():
    layout = Layout(offset_fields=3)
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["f4"]
    assert report.task.resource.stats["rows"] == 4
    assert report.task.valid


def test_validate_layout_limit_and_offset_fields():
    layout = Layout(limit_fields=2, offset_fields=1)
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["f2", "f3"]
    assert report.task.resource.stats["rows"] == 4
    assert report.task.valid


def test_validate_layout_pick_rows():
    layout = Layout(pick_rows=[1, 3, "31"])
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["f1", "f2", "f3", "f4"]
    assert report.task.resource.stats["rows"] == 2
    assert report.task.valid


def test_validate_layout_pick_rows_regex():
    layout = Layout(pick_rows=["<regex>[f23]1"])
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["f1", "f2", "f3", "f4"]
    assert report.task.resource.stats["rows"] == 2
    assert report.task.valid


def test_validate_layout_skip_rows():
    layout = Layout(skip_rows=[2, "41"])
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["f1", "f2", "f3", "f4"]
    assert report.task.resource.stats["rows"] == 2
    assert report.task.valid


def test_validate_layout_skip_rows_regex():
    layout = Layout(skip_rows=["<regex>[14]1"])
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["f1", "f2", "f3", "f4"]
    assert report.task.resource.stats["rows"] == 2
    assert report.task.valid


def test_validate_layout_skip_rows_blank():
    layout = Layout(skip_rows=["<blank>"])
    resource = Resource("data/blank-rows.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["id", "name", "age"]
    assert report.task.resource.stats["rows"] == 2
    assert report.task.valid


def test_validate_layout_pick_rows_and_fields():
    layout = Layout(pick_rows=[1, 3, "31"], pick_fields=[2, "f3"])
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["f2", "f3"]
    assert report.task.resource.stats["rows"] == 2
    assert report.task.valid


def test_validate_layout_skip_rows_and_fields():
    layout = Layout(skip_rows=[2, "41"], skip_fields=[1, "f4"])
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["f2", "f3"]
    assert report.task.resource.stats["rows"] == 2
    assert report.task.valid


def test_validate_layout_limit_rows():
    layout = Layout(limit_rows=1)
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["f1", "f2", "f3", "f4"]
    assert report.task.resource.stats["rows"] == 1
    assert report.task.valid


def test_validate_layout_offset_rows():
    layout = Layout(offset_rows=3)
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["f1", "f2", "f3", "f4"]
    assert report.task.resource.stats["rows"] == 1
    assert report.task.valid


def test_validate_layout_limit_and_offset_rows():
    layout = Layout(limit_rows=2, offset_rows=1)
    resource = Resource("data/matrix.csv", layout=layout)
    report = resource.validate()
    assert report.task.resource.header == ["f1", "f2", "f3", "f4"]
    assert report.task.resource.stats["rows"] == 2
    assert report.task.valid


def test_validate_layout_invalid_limit_rows():
    layout = Layout(limit_rows=2)
    resource = Resource("data/invalid.csv", layout=layout)
    report = resource.validate()
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 3, "blank-label"],
        [None, 4, "duplicate-label"],
        [2, 3, "missing-cell"],
        [2, 4, "missing-cell"],
        [3, 3, "missing-cell"],
        [3, 4, "missing-cell"],
    ]


def test_validate_layout_structure_errors_with_limit_rows():
    layout = Layout(limit_rows=3)
    resource = Resource("data/structure-errors.csv", layout=layout)
    report = resource.validate()
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, None, "blank-row"],
    ]
