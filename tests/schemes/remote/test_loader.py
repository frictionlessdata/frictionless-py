import pytest

from frictionless import Dialect, platform, schemes
from frictionless.resources import TableResource

BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Read


@pytest.mark.vcr
def test_remote_loader():
    with TableResource(path=BASEURL % "data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_remote_loader_latin1():
    # Github returns wrong encoding `utf-8`
    with TableResource(path=BASEURL % "data/latin1.csv") as resource:
        assert resource.read_rows()


@pytest.mark.ci
@pytest.mark.vcr
def test_remote_loader_big_file():
    dialect = Dialect(header=False)
    with TableResource(path=BASEURL % "data/table1.csv", dialect=dialect) as resource:
        assert resource.read_rows()
        assert resource.stats.md5 == "78ea269458be04a0e02816c56fc684ef"
        assert (
            resource.stats.sha256
            == "aced987247a03e01acde64aa6b40980350b785e3aedc417ff2e09bbeacbfbf2b"
        )
        assert resource.stats.bytes == 1000000
        assert resource.stats.fields == 10
        assert resource.stats.rows == 10000


@pytest.mark.vcr
def test_remote_loader_http_preload():
    control = schemes.RemoteControl(http_preload=True)
    with TableResource(path=BASEURL % "data/table.csv", control=control) as resource:
        control = resource.dialect.get_control("remote")
        assert isinstance(control, schemes.RemoteControl)
        assert control.http_preload is True
        assert resource.sample == [["id", "name"], ["1", "english"], ["2", "中国人"]]
        assert resource.fragment == [["1", "english"], ["2", "中国人"]]
        assert resource.header == ["id", "name"]


# Write


# NOTE:
# This test only checks the POST request the loader makes
# We need fully mock a session with a server or use a real one and vcr.py
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_remote_loader_write(requests_mock):
    path = "https://example.com/post/table.csv"
    requests_mock.post("https://example.com/post/")
    source = TableResource(path="data/table.csv")
    target = source.write(path)
    assert target


# Bugs


@pytest.mark.vcr
def test_remote_loader_if_remote_basepath_and_file_scheme_issue_1388():
    resource = TableResource(path="table.csv", scheme="file", basepath=BASEURL % "data")
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
