import pytest
from frictionless import Resource


BASE_URL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Read


@pytest.mark.vcr
def test_remote_loader():
    with Resource(BASE_URL % "data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# TODO: enable when loader.buffer is implemented
@pytest.mark.skip
@pytest.mark.vcr
def test_remote_loader_latin1():
    # Github returns wrong encoding `utf-8`
    with Resource(BASE_URL % "data/latin1.csv") as resource:
        assert resource.read_rows()


@pytest.mark.ci
@pytest.mark.vcr
def test_remote_loader_big_file():
    with Resource(BASE_URL % "data/table1.csv") as resource:
        assert resource.read_rows()
        assert resource.stats == {
            "hash": "78ea269458be04a0e02816c56fc684ef",
            "bytes": 1000000,
            "fields": 10,
            "rows": 10000,
        }


# Write


# NOTE:
# This test only checks the POST request the loader makes
# We need fully mock a session with a server or use a real one and vcr.py
def test_remote_loader_write(requests_mock):
    path = "https://example.com/post/table.csv"
    requests_mock.post("https://example.com/post/")
    source = Resource("data/table.csv")
    target = source.write(path)
    assert target
