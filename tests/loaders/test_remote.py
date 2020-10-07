import pytest
from frictionless import Table

BASE_URL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Read


@pytest.mark.ci
def test_table_https():
    with Table(BASE_URL % "data/table.csv") as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


@pytest.mark.ci
def test_table_https_latin1():
    # Github returns wrong encoding `utf-8`
    with Table(BASE_URL % "data/latin1.csv") as table:
        assert table.read_data()


@pytest.mark.ci
def test_table_https_big_file():
    with Table(BASE_URL % "data/table1.csv") as table:
        assert table.read_rows()
        assert table.stats == {
            "hash": "78ea269458be04a0e02816c56fc684ef",
            "bytes": 1000000,
            "fields": 10,
            "rows": 10000,
        }
