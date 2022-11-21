import pytest
from datetime import datetime, time
from frictionless import Resource, formats, platform


# General


@pytest.mark.skipif(platform.type == "darwin", reason="Skip SQL test in MacOS")
@pytest.mark.skipif(platform.type == "windows", reason="Skip SQL test in Windows")
def test_sql_parser_write_timezone_postgresql(postgresql_url):
    source = Resource("data/timezone.csv")
    control = formats.SqlControl(table="timezone")
    target = source.write(postgresql_url, control=control)
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


@pytest.mark.skipif(platform.type == "darwin", reason="Skip SQL test in MacOS")
@pytest.mark.skipif(platform.type == "windows", reason="Skip SQL test in Windows")
def test_sql_parser_write_string_pk_issue_777_postgresql(postgresql_url):
    source = Resource("data/table.csv")
    source.infer()
    source.schema.primary_key = ["name"]
    control = formats.SqlControl(table="name")
    target = source.write(postgresql_url, control=control)
    with target:
        assert target.schema.primary_key == ["name"]
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
