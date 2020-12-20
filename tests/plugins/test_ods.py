import pytest
from datetime import datetime
from frictionless import Table, Query, FrictionlessException, helpers
from frictionless.plugins.ods import OdsDialect

BASE_URL = "https://raw.githubusercontent.com/okfn/tabulator-py/master/%s"


# Parser


def test_ods_parser():
    with Table("data/table.ods") as table:
        assert table.format == "ods"
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_ods_parser_remote():
    source = BASE_URL % "data/table.ods"
    with Table(source) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_ods_parser_sheet_by_index():
    dialect = OdsDialect(sheet=1)
    with Table("data/table.ods", dialect=dialect) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_ods_parser_sheet_by_index_not_existent():
    dialect = OdsDialect(sheet=3)
    table = Table("data/table.ods", dialect=dialect)
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "format-error"
    assert error.note == 'OpenOffice document "data/table.ods" does not have a sheet "3"'


def test_ods_parser_sheet_by_name():
    dialect = OdsDialect(sheet="Лист1")
    with Table("data/table.ods", dialect=dialect) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_ods_parser_sheet_by_name_not_existent():
    dialect = OdsDialect(sheet="bad")
    table = Table("data/table.ods", dialect=dialect)
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "format-error"
    assert (
        error.note == 'OpenOffice document "data/table.ods" does not have a sheet "bad"'
    )


def test_ods_parser_with_boolean():
    with Table("data/table-with-booleans.ods") as table:
        assert table.header == ["id", "boolean"]
        assert table.read_rows() == [
            {"id": 1, "boolean": True},
            {"id": 2, "boolean": False},
        ]


def test_ods_parser_with_ints_floats_dates():
    source = "data/table-with-ints-floats-dates.ods"
    with Table(source) as table:
        assert table.read_data() == [
            ["Int", "Float", "Date", "Datetime"],
            [2013, 3.3, datetime(2009, 8, 16).date(), datetime(2009, 8, 16, 5, 43, 21)],
            [1997, 5.6, datetime(2009, 9, 20).date(), datetime(2009, 9, 20, 15, 30, 0)],
            [1969, 11.7, datetime(2012, 8, 23).date(), datetime(2012, 8, 23, 20, 40, 59)],
        ]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_table_write_ods(tmpdir):
    source = "data/table.csv"
    target = str(tmpdir.join("table.ods"))
    with Table(source) as table:
        table.write(target)
    # TODO: fix ezodf writer creates more cells than we ask (remove limits)
    query = Query(limit_fields=2, limit_rows=2)
    with Table(target, query=query) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
