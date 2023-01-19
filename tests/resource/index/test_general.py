import pytest
import sqlalchemy as sa
from frictionless import Resource, platform


# Sqlite


def test_resource_index_sqlite(sqlite_url):
    engine = sa.create_engine(sqlite_url)
    resource = Resource("data/table.csv")
    resource.index(sqlite_url, table_name="table")
    assert list(engine.execute('SELECT * FROM "table"')) == [
        (1, "english"),
        (2, "中国人"),
    ]


@pytest.mark.skipif(platform.type == "darwin", reason="Skip SQL test in MacOS")
@pytest.mark.skipif(platform.type == "windows", reason="Skip SQL test in Windows")
def test_resource_index_sqlite_fast(sqlite_url):
    engine = sa.create_engine(sqlite_url)
    resource = Resource("data/table.csv")
    resource.index(sqlite_url, table_name="table2", fast=True)
    assert list(engine.execute('SELECT * FROM "table2"')) == [
        (1, "english"),
        (2, "中国人"),
    ]


# Postgres


def test_resource_index_postgres(postgresql_url):
    engine = sa.create_engine(postgresql_url)
    resource = Resource("data/table.csv")
    resource.index(postgresql_url, table_name="table")
    assert list(engine.execute('SELECT * FROM "table"')) == [
        (1, "english"),
        (2, "中国人"),
    ]


@pytest.mark.skipif(platform.type == "darwin", reason="Skip SQL test in MacOS")
@pytest.mark.skipif(platform.type == "windows", reason="Skip SQL test in Windows")
def test_resource_index_postgres_fast(postgresql_url):
    engine = sa.create_engine(postgresql_url)
    resource = Resource("data/table.csv")
    resource.index(postgresql_url, table_name="table", fast=True)
    assert list(engine.execute('SELECT * FROM "table"')) == [
        (1, "english"),
        (2, "中国人"),
    ]
