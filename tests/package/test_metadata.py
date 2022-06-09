import pytest
from frictionless import Package, Resource, helpers
from frictionless import FrictionlessException


IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Metadata


@pytest.mark.vcr
def test_package_external_profile():
    profile = "frictionless/assets/profiles/package/general.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package(resources=[resource], profile=profile)
    assert package.metadata_valid


@pytest.mark.vcr
def test_package_external_profile_invalid_local():
    profile = "data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package(resources=[resource], profile=profile)
    assert len(package.metadata_errors) == 5
    for error in package.metadata_errors:
        assert "required" in error.message


@pytest.mark.vcr
def test_package_external_profile_invalid_local_from_descriptor():
    profile = "data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package({"resources": [resource.to_dict()], "profile": profile})
    assert len(package.metadata_errors) == 5
    for error in package.metadata_errors:
        assert "required" in error.message


@pytest.mark.vcr
def test_package_external_profile_invalid_local_from_descriptor_unsafe():
    profile = "data/../data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package({"resources": [resource.to_dict()], "profile": profile})
    if IS_UNIX:
        with pytest.raises(FrictionlessException):
            package.metadata_errors


@pytest.mark.vcr
def test_package_external_profile_invalid_local_from_descriptor_unsafe_trusted():
    profile = "data/../data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package({"resources": [resource.to_dict()], "profile": profile})
    package.trusted = True
    assert len(package.metadata_errors) == 5
    for error in package.metadata_errors:
        assert "required" in error.message


@pytest.mark.vcr
def test_package_external_profile_invalid_remote():
    profile = (
        "https://raw.githubusercontent.com/tdwg/camtrap-dp/main/camtrap-dp-profile.json"
    )
    resource = Resource(name="table", path="data/table.csv")
    package = Package(resources=[resource], profile=profile)
    assert len(package.metadata_errors) == 5
    for error in package.metadata_errors:
        assert "required" in error.message


@pytest.mark.vcr
def test_package_external_profile_invalid_remote_from_descriptor():
    profile = (
        "https://raw.githubusercontent.com/tdwg/camtrap-dp/main/camtrap-dp-profile.json"
    )
    resource = Resource(name="table", path="data/table.csv")
    package = Package({"resources": [resource.to_dict()], "profile": profile})
    assert len(package.metadata_errors) == 5
    for error in package.metadata_errors:
        assert "required" in error.message
