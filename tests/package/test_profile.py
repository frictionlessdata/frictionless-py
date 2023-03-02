import pytest
from frictionless import Package, Resource, FrictionlessException, system


# General


@pytest.mark.vcr
def test_package_profiles_invalid_local():
    profile = "data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package(resources=[resource], profile=profile)
    with pytest.raises(FrictionlessException) as excinfo:
        package.to_descriptor()
    reasons = excinfo.value.reasons
    assert len(reasons) == 5
    for error in reasons:
        assert "required" in error.message


@pytest.mark.vcr
def test_package_profiles_invalid_local_from_descriptor():
    profile = "data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        Package({"resources": [resource.to_descriptor()], "profile": profile})
    reasons = excinfo.value.reasons
    assert len(reasons) == 5
    for error in reasons:
        assert "required" in error.message


@pytest.mark.vcr
def test_package_external_profile_invalid_remote():
    profile = (
        "https://raw.githubusercontent.com/tdwg/camtrap-dp/main/camtrap-dp-profile.json"
    )
    resource = Resource(name="table", path="data/table.csv")
    package = Package(resources=[resource], profile=profile)
    with pytest.raises(FrictionlessException) as excinfo:
        package.to_descriptor()
    reasons = excinfo.value.reasons
    assert len(reasons) == 5
    for error in reasons:
        assert "required" in error.message


@pytest.mark.vcr
def test_package_external_profile_invalid_remote_from_descriptor():
    profile = (
        "https://raw.githubusercontent.com/tdwg/camtrap-dp/main/camtrap-dp-profile.json"
    )
    resource = Resource(name="table", path="data/table.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        Package({"resources": [resource.to_descriptor()], "profile": profile})
    reasons = excinfo.value.reasons
    assert len(reasons) == 5
    for error in reasons:
        assert "required" in error.message


@pytest.mark.parametrize("profile", ["data-package", "tabular-data-package"])
def test_package_profile_type(profile):
    descriptor = {
        "resources": [{"name": "table", "path": "data/table.csv"}],
        "profile": profile,
    }
    package = Package.from_descriptor(descriptor)
    descriptor = package.to_descriptor()
    assert descriptor.get("profile") is None


# Legacy


@pytest.mark.vcr
def test_package_profiles_from_descriptor_standards_v1():
    profile = "data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        Package({"resources": [resource.to_descriptor()], "profile": profile})
    reasons = excinfo.value.reasons
    assert len(reasons) == 5
    for error in reasons:
        assert "required" in error.message


@pytest.mark.skip
@pytest.mark.vcr
def test_package_profiles_to_descriptor_standards_v1():
    profile = "data/profiles/empty.json"
    descriptor = {
        "resources": [{"name": "table", "path": "data/table.csv"}],
        "profiles": [profile],
    }
    package = Package.from_descriptor(descriptor)
    with system.use_context(standards="v1"):
        descriptor = package.to_descriptor()
        assert descriptor["profile"] == profile
