from datetime import datetime, time

import pytest

from frictionless import Dialect, FrictionlessException, formats, platform
from frictionless.resources import TableResource

pytestmark = pytest.mark.skipif(
    platform.type == "windows",
    reason="Duckdb not supported on windows",
)


# Read


def test_sql_parser(duckdb_url_data):
    control = formats.SqlControl(table="table")
    with TableResource(path=duckdb_url_data, control=control) as resource:
        assert resource.schema.to_descriptor() == {
            "fields": [
                {"name": "id", "type": "integer", "constraints": {"required": True}},
                {"name": "name", "type": "string"},
            ],
            # TODO: add indicies support
            # DuckDBEngineWarning: duckdb-engine doesn't yet support reflection on indices
            # https://github.com/Mause/duckdb_engine/blob/71b1ed2f63dc25a848995986401be765711d763d/duckdb_engine/__init__.py#L159
            #  "primaryKey": ["id"],
        }
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_order_by(duckdb_url_data):
    control = formats.SqlControl(table="table", order_by="id")
    with TableResource(path=duckdb_url_data, control=control) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_order_by_desc(duckdb_url_data):
    control = formats.SqlControl(table="table", order_by="id desc")
    with TableResource(path=duckdb_url_data, control=control) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 2, "name": "中国人"},
            {"id": 1, "name": "english"},
        ]


def test_sql_parser_where(duckdb_url_data):
    control = formats.SqlControl(table="table", where="name = '中国人'")
    with TableResource(path=duckdb_url_data, control=control) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_table_is_required_error(duckdb_url_data):
    resource = TableResource(path=duckdb_url_data)
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.type == "error"
    assert error.note.count('Please provide "dialect.sql.table" for reading')


# The output is quite weird but it's a correct output for SQL with header=False
def test_sql_parser_header_false(duckdb_url_data):
    control = formats.SqlControl(table="table")
    dialect = Dialect(header=False, controls=[control])
    with TableResource(path=duckdb_url_data, dialect=dialect) as resource:
        assert resource.header.missing
        assert resource.read_rows() == [
            {"id": None, "name": "name"},
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Write


def test_sql_parser_write(duckdb_url_data):
    source = TableResource(path="data/table.csv")
    control = formats.SqlControl(table="name", order_by="id")
    target = source.write(path=duckdb_url_data, control=control)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_write_where(duckdb_url_data):
    source = TableResource(path="data/table.csv")
    control = formats.SqlControl(table="name", where="name = '中国人'")
    target = source.write(path=duckdb_url_data, control=control)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_write_timezone(sqlite_url):
    source = TableResource(path="data/timezone.csv")
    control = formats.SqlControl(table="timezone")
    target = source.write(path=sqlite_url, control=control)
    with target:
        assert target.header == ["datetime", "time"]
        assert target.read_rows() == [
            {
                "datetime": datetime(2020, 1, 1, 15),
                "time": time(15),
            },
            {
                "datetime": datetime(2020, 1, 1, 15),
                "time": time(15),
            },
            {
                "datetime": datetime(2020, 1, 1, 12),
                "time": time(12),
            },
            {
                "datetime": datetime(2020, 1, 1, 18),
                "time": time(18),
            },
        ]


# Bugs


def test_sql_parser_write_string_pk_issue_777_sqlite(sqlite_url):
    source = TableResource(path="data/table.csv")
    source.infer()
    source.schema.primary_key = ["name"]
    control = formats.SqlControl(table="name")
    target = source.write(path=sqlite_url, control=control)
    with target:
        assert target.schema.primary_key == ["name"]
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_sql_parser_describe_to_yaml_failing_issue_821(duckdb_url_data):
    control = formats.SqlControl(table="table")
    resource = TableResource(path=duckdb_url_data, control=control)
    resource.infer()
    assert resource.to_yaml()
