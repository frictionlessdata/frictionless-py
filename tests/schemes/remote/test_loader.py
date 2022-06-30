import pytest
from frictionless import Resource, Dialect
from frictionless.plugins.remote import RemoteControl


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Read


@pytest.mark.vcr
def test_remote_loader():
    with Resource(BASEURL % "data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_remote_loader_latin1():
    # Github returns wrong encoding `utf-8`
    with Resource(BASEURL % "data/latin1.csv") as resource:
        assert resource.read_rows()


@pytest.mark.ci
@pytest.mark.vcr
def test_remote_loader_big_file():
    dialect = Dialect(header=False)
    with Resource(BASEURL % "data/table1.csv", dialect=dialect) as resource:
        assert resource.read_rows()
        assert resource.stats == {
            "hash": "78ea269458be04a0e02816c56fc684ef",
            "bytes": 1000000,
            "fields": 10,
            "rows": 10000,
        }


@pytest.mark.vcr
def test_remote_loader_http_preload():
    dialect = Dialect(controls=[RemoteControl(http_preload=True)])
    with Resource(BASEURL % "data/table.csv", dialect=dialect) as resource:
        assert resource.dialect.get_control("remote").http_preload is True
        assert resource.sample == [["id", "name"], ["1", "english"], ["2", "中国人"]]
        assert resource.fragment == [["1", "english"], ["2", "中国人"]]
        assert resource.header == ["id", "name"]


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
