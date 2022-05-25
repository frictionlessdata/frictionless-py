import pytest
import datetime
from frictionless import Resource, Layout, FrictionlessException
from frictionless.plugins.sql import SqlDialect


# General


def test_sql_parser(database_url):
    dialect = SqlDialect(table="table")
    with Resource(database_url, dialect=dialect) as resource:
        assert resource.schema == {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ],
            "primaryKey": ["id"],
        }
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_order_by(database_url):
    dialect = SqlDialect(table="table", order_by="id")
    with Resource(database_url, dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_order_by_desc(database_url):
    dialect = SqlDialect(table="table", order_by="id desc")
    with Resource(database_url, dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 2, "name": "中国人"},
            {"id": 1, "name": "english"},
        ]


def test_sql_parser_where(database_url):
    dialect = SqlDialect(table="table", where="name = '中国人'")
    with Resource(database_url, dialect=dialect) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_table_is_required_error(database_url):
    resource = Resource(database_url)
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "dialect-error"
    assert error.note.count("'table' is a required property")


# NOTE: Probably it's not correct behaviour
def test_sql_parser_headers_false(database_url):
    dialect = SqlDialect(table="table")
    layout = Layout(header=False)
    with Resource(database_url, dialect=dialect, layout=layout) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": None, "name": "name"},
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_write(database_url):
    source = Resource("data/table.csv")
    target = source.write(database_url, dialect=SqlDialect(table="name", order_by="id"))
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_write_where(database_url):
    source = Resource("data/table.csv")
    target = source.write(
        database_url, dialect=SqlDialect(table="name", where="name = '中国人'")
    )
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 2, "name": "中国人"},
        ]


# TODO: add timezone support or document if it's not possible
def test_sql_parser_write_timezone(sqlite_url):
    source = Resource("data/timezone.csv")
    target = source.write(sqlite_url, dialect=SqlDialect(table="timezone"))
    with target:
        assert target.header == ["datetime", "time"]
        assert target.read_rows() == [
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
        ]


def test_sql_parser_write_string_pk_issue_777_sqlite(sqlite_url):
    source = Resource("data/table.csv")
    source.infer()
    source.schema.primary_key = ["name"]
    target = source.write(sqlite_url, dialect=SqlDialect(table="name"))
    with target:
        assert target.schema.primary_key == ["name"]
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# The resource.to_yaml call was failing before the fix (see the issue)
def test_sql_parser_describe_to_yaml_issue_821(database_url):
    dialect = SqlDialect(table="table")
    resource = Resource(database_url, dialect=dialect)
    resource.infer()
    assert resource.to_yaml()
