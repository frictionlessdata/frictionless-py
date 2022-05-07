import pytest
from frictionless import Resource, Layout, helpers


IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Stats


def test_resource_stats_hash():
    with Resource("data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.hashing == "md5"
        if IS_UNIX:
            assert resource.stats["hash"] == "d82306001266c4343a2af4830321ead8"


def test_resource_stats_hash_md5():
    with Resource("data/doublequote.csv", hashing="md5") as resource:
        resource.read_rows()
        assert resource.hashing == "md5"
        if IS_UNIX:
            assert resource.stats["hash"] == "d82306001266c4343a2af4830321ead8"


def test_resource_stats_hash_sha1():
    with Resource("data/doublequote.csv", hashing="sha1") as resource:
        resource.read_rows()
        assert resource.hashing == "sha1"
        if IS_UNIX:
            assert resource.stats["hash"] == "2842768834a6804d8644dd689da61c7ab71cbb33"


def test_resource_stats_hash_sha256():
    with Resource("data/doublequote.csv", hashing="sha256") as resource:
        resource.read_rows()
        assert resource.hashing == "sha256"
        if IS_UNIX:
            assert (
                resource.stats["hash"]
                == "41fdde1d8dbcb3b2d4a1410acd7ad842781f076076a73b049863d6c1c73868db"
            )


def test_resource_stats_hash_sha512():
    with Resource("data/doublequote.csv", hashing="sha512") as resource:
        resource.read_rows()
        assert resource.hashing == "sha512"
        if IS_UNIX:
            assert (
                resource.stats["hash"]
                == "fa555b28a01959c8b03996cd4757542be86293fd49641d61808e4bf9fe4115619754aae9ae6af6a0695585eaade4488ce00dfc40fc4394b6376cd20d6967769c"
            )


def test_resource_stats_hash_compressed():
    with Resource("data/doublequote.csv.zip") as resource:
        resource.read_rows()
        assert resource.hashing == "md5"
        if IS_UNIX:
            assert resource.stats["hash"] == "2a72c90bd48c1fa48aec632db23ce8f7"


@pytest.mark.vcr
def test_resource_stats_hash_remote():
    with Resource(BASEURL % "data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.hashing == "md5"
        if IS_UNIX:
            assert resource.stats["hash"] == "d82306001266c4343a2af4830321ead8"


def test_resource_stats_bytes():
    with Resource("data/doublequote.csv") as resource:
        resource.read_rows()
        if IS_UNIX:
            assert resource.stats["bytes"] == 7346


def test_resource_stats_bytes_compressed():
    with Resource("data/doublequote.csv.zip") as resource:
        resource.read_rows()
        if IS_UNIX:
            assert resource.stats["bytes"] == 1265


@pytest.mark.vcr
def test_resource_stats_bytes_remote():
    with Resource(BASEURL % "data/doublequote.csv") as resource:
        resource.read_rows()
        if IS_UNIX:
            assert resource.stats["bytes"] == 7346


def test_resource_stats_fields():
    with Resource("data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats["fields"] == 17
        resource.open()
        resource.read_rows()
        assert resource.stats["fields"] == 17


@pytest.mark.vcr
def test_resource_stats_fields_remote():
    with Resource(BASEURL % "data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats["fields"] == 17


def test_resource_stats_rows():
    with Resource("data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats["rows"] == 5
        resource.open()
        resource.read_rows()
        assert resource.stats["rows"] == 5


@pytest.mark.vcr
def test_resource_stats_rows_remote():
    with Resource(BASEURL % "data/doublequote.csv") as resource:
        resource.read_rows()
        assert resource.stats["rows"] == 5


def test_resource_stats_rows_significant():
    layout = Layout(header=False)
    with Resource("data/table-1MB.csv", layout=layout) as resource:
        print(resource.read_rows())
        assert resource.stats["rows"] == 10000
