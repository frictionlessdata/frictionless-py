import datetime
from frictionless import Resource
from frictionless.plugins.sql import SqlDialect


# General


# TODO: add timezone support or document if it's not possible
def test_sql_parser_write_timezone_postgresql(postgresql_url):
    source = Resource("data/timezone.csv")
    target = source.write(postgresql_url, dialect=SqlDialect(table="timezone"))
    with target:
        assert target.header == ["datetime", "time"]
        assert target.read_rows() == [
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
        ]


def test_sql_parser_write_string_pk_issue_777_postgresql(postgresql_url):
    source = Resource("data/table.csv")
    source.infer()
    source.schema.primary_key = ["name"]
    target = source.write(postgresql_url, dialect=SqlDialect(table="name"))
    with target:
        assert target.schema.primary_key == ["name"]
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
