import pytest
from frictionless import Table

BASE_URL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Read


@pytest.mark.vcr
def test_remote_loader():
    with Table(BASE_URL % "data/table.csv") as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


@pytest.mark.vcr
def test_remote_loader_latin1():
    # Github returns wrong encoding `utf-8`
    with Table(BASE_URL % "data/latin1.csv") as table:
        assert table.read_data()


@pytest.mark.ci
@pytest.mark.vcr
def test_remote_loader_big_file():
    with Table(BASE_URL % "data/table1.csv") as table:
        assert table.read_rows()
        assert table.stats == {
            "hash": "78ea269458be04a0e02816c56fc684ef",
            "bytes": 1000000,
            "fields": 10,
            "rows": 10000,
        }


# Write


# This test only checks the POST request the loader makes
# We need fully mock a session with a server or use a real one and vcr.py
def test_remote_loader_write(requests_mock):
    path = "https://example.com/post/table.csv"
    requests_mock.post("https://example.com/post/")
    with Table("data/table.csv") as table:
        response = table.write(path)
    assert response.status_code == 200
