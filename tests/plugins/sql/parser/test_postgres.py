import datetime
from frictionless import Resource, Dialect
from frictionless.plugins.sql import SqlControl


# General


# TODO: add timezone support or document if it's not possible
def test_sql_parser_write_timezone_postgresql(postgresql_url):
    source = Resource("data/timezone.csv")
    dialect = Dialect(controls=[SqlControl(table="timezone")])
    target = source.write(postgresql_url, dialect=dialect)
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
    dialect = Dialect(controls=[SqlControl(table="name")])
    target = source.write(postgresql_url, dialect=dialect)
    with target:
        assert target.schema.primary_key == ["name"]
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
