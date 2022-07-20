from frictionless import Resource, Dialect, formats


# General


def test_resource_validate_dialect_delimiter():
    control = formats.CsvControl(delimiter=";")
    resource = Resource("data/delimiter.csv", control=control)
    report = resource.validate()
    assert report.valid
    assert report.task.stats.rows == 2


def test_resource_validate_dialect_header_false():
    dialect = Dialect(header=False)
    resource = Resource("data/without-headers.csv", dialect=dialect)
    report = resource.validate()
    assert report.valid
    assert report.task.stats.rows == 3
    assert resource.dialect.header is False
    assert resource.labels == []
    assert resource.header == ["field1", "field2"]


def test_resource_validate_dialect_none_extra_cell():
    dialect = Dialect(header=False)
    resource = Resource("data/without-headers-extra.csv", dialect=dialect)
    report = resource.validate()
    assert report.task.stats.rows == 3
    assert resource.dialect.header is False
    assert resource.labels == []
    assert resource.header == ["field1", "field2"]
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [3, 3, "extra-cell"],
    ]


def test_resource_validate_dialect_number():
    dialect = Dialect(header_rows=[2])
    resource = Resource("data/matrix.csv", dialect=dialect)
    report = resource.validate()
    assert resource.header == ["11", "12", "13", "14"]
    assert report.valid


def test_resource_validate_dialect_list_of_numbers():
    dialect = Dialect(header_rows=[2, 3, 4])
    resource = Resource("data/matrix.csv", dialect=dialect)
    report = resource.validate()
    assert resource.header == ["11 21 31", "12 22 32", "13 23 33", "14 24 34"]
    assert report.valid


def test_resource_validate_dialect_list_of_numbers_and_headers_join():
    dialect = Dialect(header_rows=[2, 3, 4], header_join=".")
    resource = Resource("data/matrix.csv", dialect=dialect)
    report = resource.validate()
    assert resource.header == ["11.21.31", "12.22.32", "13.23.33", "14.24.34"]
    assert report.valid


def test_resource_validate_dialect_skip_rows():
    dialect = Dialect(comment_char="41", comment_rows=[2])
    resource = Resource("data/matrix.csv", dialect=dialect)
    report = resource.validate()
    assert resource.header == ["f1", "f2", "f3", "f4"]
    assert report.task.stats.rows == 2
    assert report.task.valid
