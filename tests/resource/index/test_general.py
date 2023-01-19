import pytest
from frictionless import Resource, platform, formats

control = formats.sql.SqlControl(table="table")

# Sqlite


def test_resource_index_sqlite(sqlite_url):
    resource = Resource("data/table.csv")
    resource.index(sqlite_url, table_name=control.table)
    assert Resource(sqlite_url, control=control).extract() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.skipif(platform.type == "windows", reason="Skip SQL test in Windows")
def test_resource_index_sqlite_fast(sqlite_url):
    resource = Resource("data/table.csv")
    resource.index(sqlite_url, table_name=control.table, fast=True)
    assert Resource(sqlite_url, control=control).extract() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.skipif(platform.type == "windows", reason="Skip SQL test in Windows")
def test_resource_index_sqlite_fast_with_use_fallback(sqlite_url):
    resource = Resource("data/table.csv")
    resource.infer()
    resource.schema.set_field_type("name", "integer")
    resource.index(sqlite_url, table_name=control.table, fast=True, use_fallback=True)
    assert Resource(sqlite_url, control=control).extract() == [
        {"id": 1, "name": None},
        {"id": 2, "name": None},
    ]


def test_resource_index_sqlite_on_progress(sqlite_url, mocker):
    on_progress = mocker.stub(name="on_progress")
    resource = Resource("data/table.csv")
    resource.index(sqlite_url, table_name=control.table, on_progress=on_progress)
    assert on_progress.call_count == 2
    on_progress.assert_any_call("1 rows")
    on_progress.assert_any_call("2 rows")


# Postgres


def test_resource_index_postgres(postgresql_url):
    resource = Resource("data/table.csv")
    resource.index(postgresql_url, table_name=control.table)
    assert Resource(postgresql_url, control=control).extract() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.skipif(platform.type == "windows", reason="Skip SQL test in Windows")
def test_resource_index_postgres_fast(postgresql_url):
    resource = Resource("data/table.csv")
    resource.index(postgresql_url, table_name=control.table, fast=True)
    assert Resource(postgresql_url, control=control).extract() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.skipif(platform.type == "windows", reason="Skip SQL test in Windows")
def test_resource_index_postgresql_fast_with_use_fallback(postgresql_url):
    resource = Resource("data/table.csv")
    resource.infer()
    resource.schema.set_field_type("name", "integer")
    resource.index(postgresql_url, table_name=control.table, fast=True, use_fallback=True)
    assert Resource(postgresql_url, control=control).extract() == [
        {"id": 1, "name": None},
        {"id": 2, "name": None},
    ]
