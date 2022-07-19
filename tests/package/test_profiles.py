import pytest
from frictionless import FrictionlessException, Package, Resource, platform


# General


@pytest.mark.vcr
@pytest.mark.xfail(reason="Profiles are not yet supported")
def test_package_external_profile():
    profile = "frictionless/assets/profiles/package/general.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package(resources=[resource], profile=profile)  # type: ignore
    assert package.metadata_valid


@pytest.mark.vcr
@pytest.mark.xfail(reason="Profiles are not yet supported")
def test_package_external_profile_invalid_local():
    profile = "data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package(resources=[resource], profile=profile)  # type: ignore
    assert len(package.metadata_errors) == 5
    for error in package.metadata_errors:
        assert "required" in error.message


@pytest.mark.vcr
@pytest.mark.xfail(reason="Profiles are not yet supported")
def test_package_external_profile_invalid_local_from_descriptor():
    profile = "data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package({"resources": [resource.to_dict()], "profile": profile})
    assert len(package.metadata_errors) == 5
    for error in package.metadata_errors:
        assert "required" in error.message


@pytest.mark.vcr
@pytest.mark.xfail(reason="Profiles are not yet supported")
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_package_external_profile_invalid_local_from_descriptor_unsafe():
    profile = "data/../data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package({"resources": [resource.to_dict()], "profile": profile})
    with pytest.raises(FrictionlessException):
        package.metadata_errors


@pytest.mark.vcr
@pytest.mark.xfail(reason="Profiles are not yet supported")
def test_package_external_profile_invalid_local_from_descriptor_unsafe_trusted():
    profile = "data/../data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package({"resources": [resource.to_dict()], "profile": profile})
    package.trusted = True
    assert len(package.metadata_errors) == 5
    for error in package.metadata_errors:
        assert "required" in error.message


@pytest.mark.vcr
@pytest.mark.xfail(reason="Profiles are not yet supported")
def test_package_external_profile_invalid_remote():
    profile = (
        "https://raw.githubusercontent.com/tdwg/camtrap-dp/main/camtrap-dp-profile.json"
    )
    resource = Resource(name="table", path="data/table.csv")
    package = Package(resources=[resource], profile=profile)  # type: ignore
    assert len(package.metadata_errors) == 5
    for error in package.metadata_errors:
        assert "required" in error.message


@pytest.mark.vcr
@pytest.mark.xfail(reason="Profiles are not yet supported")
def test_package_external_profile_invalid_remote_from_descriptor():
    profile = (
        "https://raw.githubusercontent.com/tdwg/camtrap-dp/main/camtrap-dp-profile.json"
    )
    resource = Resource(name="table", path="data/table.csv")
    package = Package({"resources": [resource.to_dict()], "profile": profile})
    assert len(package.metadata_errors) == 5
    for error in package.metadata_errors:
        assert "required" in error.message
