import pytest
from datetime import datetime
from frictionless import Resource, Layout, FrictionlessException
from frictionless.plugins.ods import OdsDialect

BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


def test_ods_parser():
    with Resource("data/table.ods") as resource:
        assert resource.format == "ods"
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_ods_parser_remote():
    source = BASEURL % "data/table.ods"
    with Resource(source) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_ods_parser_sheet_by_index():
    dialect = OdsDialect(sheet=1)
    with Resource("data/table.ods", dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_ods_parser_sheet_by_index_not_existent():
    dialect = OdsDialect(sheet=3)
    resource = Resource("data/table.ods", dialect=dialect)
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "format-error"
    assert error.note == 'OpenOffice document "data/table.ods" does not have a sheet "3"'


def test_ods_parser_sheet_by_name():
    dialect = OdsDialect(sheet="Лист1")
    with Resource("data/table.ods", dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_ods_parser_sheet_by_name_not_existent():
    dialect = OdsDialect(sheet="bad")
    table = Resource("data/table.ods", dialect=dialect)
    with pytest.raises(FrictionlessException) as excinfo:
        table.open()
    error = excinfo.value.error
    assert error.code == "format-error"
    assert (
        error.note == 'OpenOffice document "data/table.ods" does not have a sheet "bad"'
    )


def test_ods_parser_with_boolean():
    with Resource("data/table-with-booleans.ods") as resource:
        assert resource.header == ["id", "boolean"]
        assert resource.read_rows() == [
            {"id": 1, "boolean": True},
            {"id": 2, "boolean": False},
        ]


def test_ods_parser_with_ints_floats_dates():
    source = "data/table-with-ints-floats-dates.ods"
    with Resource(source) as resource:
        assert resource.read_lists() == [
            ["Int", "Float", "Date", "Datetime"],
            [2013, 3.3, datetime(2009, 8, 16).date(), datetime(2009, 8, 16, 5, 43, 21)],
            [1997, 5.6, datetime(2009, 9, 20).date(), datetime(2009, 9, 20, 15, 30, 0)],
            [1969, 11.7, datetime(2012, 8, 23).date(), datetime(2012, 8, 23, 20, 40, 59)],
        ]


def test_ods_parser_write(tmpdir):
    source = Resource("data/table.csv")
    # NOTE: ezodf writer creates more cells than we ask (remove limits)
    layout = Layout(limit_fields=2, limit_rows=2)
    target = Resource(str(tmpdir.join("table.ods")), layout=layout)
    source.write(target)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
