import pytest
import yaml

from frictionless import FrictionlessException, Package, Resource, system

# General


@pytest.mark.vcr
def test_package_profiles_invalid_local():
    profile = "data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package(resources=[resource], profile=profile)
    with pytest.raises(FrictionlessException) as excinfo:
        package.to_descriptor(validate=True)
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
        package.to_descriptor(validate=True)
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


@pytest.mark.skip
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


# Bugs


def test_package_preserver_profile_issue_1480():
    descriptor = yaml.safe_load(
        """
    profile: tabular-data-package
    resources:
      -
        name: some-table
        profile: tabular-data-resource
        path: some-file.csv
        format: csv
        mediatype: text/csv
        encoding: utf-8
        schema: schema.json
    """
    )
    package = Package(descriptor)
    assert package.profile == "tabular-data-package"
    assert package.get_resource("some-table").profile == "tabular-data-resource"


def test_package_profile_tabular_requirements_issue_1484():
    descriptor = yaml.safe_load(
        """
    profile: tabular-data-package
    resources:
      -
        name: some-table
        path: some-file.csv
        format: csv
        mediatype: text/csv
        encoding: utf-8
        schema: schema.json
    """
    )
    report = Package.validate_descriptor(descriptor)
    assert report.flatten(["type", "note"]) == [
        [
            "package-error",
            'profile "tabular-data-package" requries all the resources to be "tabular-data-resource"',
        ]
    ]


def test_package_profile_tabular_requirements_schema_issue_1484():
    descriptor = yaml.safe_load(
        """
    profile: tabular-data-package
    resources:
      -
        name: some-table
        profile: tabular-data-resource
        path: some-file.csv
        format: csv
        mediatype: text/csv
        encoding: utf-8
    """
    )
    report = Package.validate_descriptor(descriptor)
    assert report.flatten(["type", "note"]) == [
        [
            "resource-error",
            'profile "tabular-data-resource" requries "schema" to be present',
        ]
    ]
