import pytest
from frictionless import FrictionlessException, Package, Resource, platform, system


# General


def test_package_profiles_invalid_local():
    profile = "data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package(resources=[resource], profiles=[profile])
    assert len(package.metadata_errors) == 5
    for error in package.metadata_errors:
        assert "required" in error.message


def test_package_profiles_invalid_local_from_descriptor():
    profile = "data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package({"resources": [resource.to_descriptor()], "profiles": [profile]})
    assert len(package.metadata_errors) == 5
    for error in package.metadata_errors:
        assert "required" in error.message


@pytest.mark.xfail(reason="safety")
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_package_external_profile_invalid_local_from_descriptor_unsafe():
    profile = "data/../data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package({"resources": [resource.to_dict()], "profile": profile})
    with pytest.raises(FrictionlessException):
        package.metadata_errors


@pytest.mark.vcr
def test_package_external_profile_invalid_local_from_descriptor_unsafe_trusted():
    profile = "data/../data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package({"resources": [resource.to_dict()], "profiles": [profile]})
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
    package = Package(resources=[resource], profiles=[profile])
    assert len(package.metadata_errors) == 5
    for error in package.metadata_errors:
        assert "required" in error.message


@pytest.mark.vcr
def test_package_external_profile_invalid_remote_from_descriptor():
    profile = (
        "https://raw.githubusercontent.com/tdwg/camtrap-dp/main/camtrap-dp-profile.json"
    )
    resource = Resource(name="table", path="data/table.csv")
    package = Package({"resources": [resource.to_dict()], "profiles": [profile]})
    assert len(package.metadata_errors) == 5
    for error in package.metadata_errors:
        assert "required" in error.message


# Legacy


def test_package_profiles_from_descriptor_v1():
    profile = "data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package({"resources": [resource.to_descriptor()], "profile": profile})
    assert len(package.metadata_errors) == 5
    for error in package.metadata_errors:
        assert "required" in error.message


def test_package_profiles_to_descriptor_v1():
    profile = "data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package(resources=[resource], profiles=[profile])
    with system.use_standards_version("v1"):
        descriptor = package.to_descriptor()
        assert descriptor["profile"] == profile
