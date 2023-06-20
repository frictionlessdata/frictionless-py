from datetime import datetime

import pytest

from frictionless import FrictionlessException, formats
from frictionless.dialect.dialect import Dialect
from frictionless.resources import TableResource

BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Read


def test_ods_parser():
    with TableResource(path="data/table.ods") as resource:
        assert resource.format == "ods"
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_ods_parser_remote():
    path = BASEURL % "data/table.ods"
    with TableResource(path=path) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_ods_parser_sheet_by_index():
    control = formats.OdsControl(sheet=1)
    with TableResource(path="data/table.ods", control=control) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_ods_parser_sheet_by_index_not_existent():
    control = formats.OdsControl(sheet=3)
    resource = TableResource(path="data/table.ods", control=control)
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.type == "format-error"
    assert error.note == 'OpenOffice document "data/table.ods" does not have a sheet "3"'


def test_ods_parser_sheet_by_name():
    control = formats.OdsControl(sheet="Лист1")
    with TableResource(path="data/table.ods", control=control) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_ods_parser_sheet_by_name_not_existent():
    control = formats.OdsControl(sheet="bad")
    table = TableResource(path="data/table.ods", control=control)
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.type == "format-error"
    assert (
        error.note == 'OpenOffice document "data/table.ods" does not have a sheet "bad"'
    )


def test_ods_parser_with_boolean():
    with TableResource(path="data/table-with-booleans.ods") as resource:
        assert resource.header == ["id", "boolean"]
        assert resource.read_rows() == [
            {"id": 1, "boolean": True},
            {"id": 2, "boolean": False},
        ]


def test_ods_parser_with_ints_floats_dates():
    path = "data/table-with-ints-floats-dates.ods"
    with TableResource(path=path) as resource:
        assert resource.read_cells() == [
            ["Int", "Float", "Date", "Datetime"],
            [2013, 3.3, datetime(2009, 8, 16).date(), datetime(2009, 8, 16, 5, 43, 21)],
            [1997, 5.6, datetime(2009, 9, 20).date(), datetime(2009, 9, 20, 15, 30, 0)],
            [1969, 11.7, datetime(2012, 8, 23).date(), datetime(2012, 8, 23, 20, 40, 59)],
        ]


# Write


def test_ods_parser_write(tmpdir):
    source = TableResource(path="data/table.csv")
    target = TableResource(path=str(tmpdir.join("table.ods")))
    source.write(target)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_ods_parser_write_skip_header(tmpdir):
    control = formats.ExcelControl(sheet="sheet")
    dialect = Dialect.from_descriptor({"header": False})
    data = b"header1,header2\nvalue11,value12\nvalue21,value22"
    path = str(tmpdir.join("table.ods"))
    target = TableResource(path=path, dialect=dialect, control=control)
    with TableResource(data=data, format="csv") as resource:
        assert resource.header == ["header1", "header2"]
        resource.write_table(target)
    table = target.read_table()
    assert table.header == ["field1", "field2"]
