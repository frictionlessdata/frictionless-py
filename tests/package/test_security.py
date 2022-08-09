import pytest
from frictionless import Package, Resource, FrictionlessException


# General


def test_package_resource_unsafe_schema():
    path = "data/table.csv"
    schema = "data/../data/schema.json"
    with pytest.raises(FrictionlessException) as excinfo:
        Package({"resources": [{"path": path, "schema": schema}]})
    error = excinfo.value.error
    assert error.type == "resource-error"
    assert error.note.count("schema.json")


def test_package_resource_unsafe_schema_trusted():
    path = "data/table.csv"
    schema = "data/../data/schema.json"
    Package({"resources": [{"path": path, "schema": schema}]}, trusted=True)


def test_package_resource_from_path_error_unsafe():
    resource = "data/../resource.json"
    with pytest.raises(FrictionlessException) as excinfo:
        Package({"resources": [resource]})
    error = excinfo.value.error
    assert error.type == "package-error"
    assert error.note.count("resource.json")


@pytest.mark.xfail(reason="security")
def test_package_external_profile_invalid_local_from_descriptor_unsafe():
    profile = "data/../data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        Package({"resources": [resource.to_descriptor()], "profile": profile})
    error = excinfo.value.error
    assert error.type == "package-error"
    assert error.note.count("camtrap.json")


@pytest.mark.xfail(reason="security")
def test_package_external_profile_invalid_local_from_descriptor_unsafe_trusted():
    profile = "data/../data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package(
        {"resources": [resource.to_descriptor()], "profiles": [profile]}, trusted=True
    )
    assert len(package.list_metadata_errors()) == 5  # type: ignore
    for error in package.list_metadata_errors():  # type: ignore
        assert "required" in error.message
