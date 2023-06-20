import pytest
from pytest_lazyfixture import lazy_fixture

from frictionless import formats, platform
from frictionless.resources import TableResource

control = formats.sql.SqlControl(table="table")
fast_database_urls = [
    lazy_fixture("sqlite_url"),
    lazy_fixture("postgresql_url"),
]
database_urls = fast_database_urls + [
    lazy_fixture("mysql_url"),
]
if platform.type != "windows":
    database_urls += [
        lazy_fixture("duckdb_url"),
    ]
pytestmark = pytest.mark.skipif(
    platform.type == "darwin" or platform.type == "windows",
    reason="Not supported tests in MacOS and Windows",
)


# General


@pytest.mark.parametrize("database_url", database_urls)
def test_resource_index_sqlite(database_url):
    assert control.table
    resource = TableResource(path="data/table.csv")
    resource.index(database_url, name=control.table)
    assert TableResource(path=database_url, control=control).read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


# With metadata


@pytest.mark.parametrize("database_url", database_urls)
def test_resource_index_sqlite_with_metadata(database_url):
    assert control.table
    resource = TableResource(path="data/table.csv")
    resource.index(database_url, name=control.table, with_metadata=True)
    assert TableResource(path=database_url, control=control).read_rows() == [
        {"_rowNumber": 2, "_rowValid": True, "id": 1, "name": "english"},
        {"_rowNumber": 3, "_rowValid": True, "id": 2, "name": "中国人"},
    ]


# Fast


@pytest.mark.ci(reason="requries sqlite3@3.34+")
@pytest.mark.parametrize("database_url", fast_database_urls)
def test_resource_index_sqlite_fast(database_url):
    assert control.table
    resource = TableResource(path="data/table.csv")
    resource.index(database_url, name=control.table, fast=True)
    assert TableResource(path=database_url, control=control).read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


# Fallback


@pytest.mark.ci(reason="requries sqlite3@3.34+")
@pytest.mark.parametrize("database_url", fast_database_urls)
def test_resource_index_sqlite_fast_with_use_fallback(database_url):
    assert control.table
    resource = TableResource(path="data/table.csv")
    resource.infer()
    resource.schema.set_field_type("name", "integer")
    resource.index(database_url, name=control.table, fast=True, use_fallback=True)
    assert TableResource(path=database_url, control=control).read_rows() == [
        {"id": 1, "name": None},
        {"id": 2, "name": None},
    ]


# On Progress


@pytest.mark.parametrize("database_url", database_urls)
def test_resource_index_sqlite_on_progress(database_url, mocker):
    assert control.table
    on_progress = mocker.stub(name="on_progress")
    resource = TableResource(path="data/table.csv")
    resource.index(database_url, name=control.table, on_progress=on_progress)
    assert on_progress.call_count == 2
    on_progress.assert_any_call(control.table, "2 rows")
    on_progress.assert_any_call(control.table, "3 rows")
