import pytest
from frictionless import Resource


@pytest.mark.xfail(reason="profiles")
def test_resource_profiles():
    resource = Resource(path="data/table.csv", profiles=["data/resource.profile.json"])
    assert resource.profiles == ["data/resource.profile.json"]
    assert resource.metadata_errors[0].type == "resource-error"
