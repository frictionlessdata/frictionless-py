import pytest
from frictionless import Resource, Dialect, platform


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_stats_hash():
    with Resource("data/doublequote.csv") as resource:
        resource.read_rows()
        assert (
            resource.stats.sha256
            == "41fdde1d8dbcb3b2d4a1410acd7ad842781f076076a73b049863d6c1c73868db"
        )


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_stats_hash_compressed():
    with Resource("data/doublequote.csv.zip") as resource:
        resource.read_rows()
        assert (
            resource.stats.sha256
            == "88d0ef9887dcd7d7800bff2981f8cc496fbfcd8704a17c2aa12a434ce7d88b13"
        )


@pytest.mark.vcr
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_stats_hash_remote():
    with Resource(BASEURL % "data/doublequote.csv") as resource:
        resource.read_rows()
        assert (
            resource.stats.sha256
            == "41fdde1d8dbcb3b2d4a1410acd7ad842781f076076a73b049863d6c1c73868db"
        )


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_stats_bytes():
    with Resource("data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats.bytes == 7346


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_stats_bytes_compressed():
    with Resource("data/doublequote.csv.zip") as resource:
        resource.read_rows()
        assert resource.stats.bytes == 1265


@pytest.mark.vcr
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_stats_bytes_remote():
    with Resource(BASEURL % "data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats.bytes == 7346


def test_resource_stats_fields():
    with Resource("data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats.fields == 17
        resource.open()
        resource.read_rows()
        assert resource.stats.fields == 17


@pytest.mark.vcr
def test_resource_stats_fields_remote():
    with Resource(BASEURL % "data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats.fields == 17


def test_resource_stats_rows():
    with Resource("data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats.rows == 5
        resource.open()
        resource.read_rows()
        assert resource.stats.rows == 5


@pytest.mark.vcr
def test_resource_stats_rows_remote():
    with Resource(BASEURL % "data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats.rows == 5


@pytest.mark.ci
def test_resource_stats_rows_significant():
    dialect = Dialect(header=False)
    with Resource("data/table-1MB.csv", dialect=dialect) as resource:
        print(resource.read_rows())
        assert resource.stats.rows == 10000
