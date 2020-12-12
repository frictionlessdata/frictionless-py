import pytest
from frictionless import Table

BASE_URL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Read


@pytest.mark.vcr()
def test_table_remote():
    with Table(BASE_URL % "data/table.csv") as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


@pytest.mark.vcr()
def test_table_remote_latin1():
    # Github returns wrong encoding `utf-8`
    with Table(BASE_URL % "data/latin1.csv") as table:
        assert table.read_data()


@pytest.mark.vcr()
def test_table_remote_big_file():
    with Table(BASE_URL % "data/table1.csv") as table:
        assert table.read_rows()
        assert table.stats == {
            "hash": "78ea269458be04a0e02816c56fc684ef",
            "bytes": 1000000,
            "fields": 10,
            "rows": 10000,
        }


# Write


# TODO: implement
@pytest.mark.skip
def test_table_remote_write():
    path = "https://example.com/post/table.csv"

    # Write
    with Table("data/table.csv") as table:
        table.write(path)

    # Read
    with Table(path) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]
