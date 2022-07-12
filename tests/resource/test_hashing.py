import pytest
from frictionless import Resource, FrictionlessException, helpers


# General


@pytest.mark.skipif(helpers.is_platform("windows"), reason="Fix on Windows")
def test_resource_hashing():
    with Resource("data/table.csv") as resource:
        resource.read_rows()
        assert resource.hashing == "md5"
        assert resource.stats["hash"] == "6c2c61dd9b0e9c6876139a449ed87933"


@pytest.mark.skipif(helpers.is_platform("windows"), reason="Fix on Windows")
def test_resource_hashing_provided():
    with Resource("data/table.csv", hashing="sha1") as resource:
        resource.read_rows()
        assert resource.hashing == "sha1"
        assert resource.stats["hash"] == "db6ea2f8ff72a9e13e1d70c28ed1c6b42af3bb0e"


def test_resource_hashing_error_bad_hashing():
    resource = Resource("data/table.csv", hashing="bad")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.type == "hashing-error"
    assert error.note == "unsupported hash type bad"
