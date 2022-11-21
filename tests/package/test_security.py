import pytest
from frictionless import Package, Resource, FrictionlessException, system, platform


# General


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_package_resource_unsafe_schema():
    path = "data/table.csv"
    schema = "data/../data/schema.json"
    with pytest.raises(FrictionlessException) as excinfo:
        Package({"resources": [{"path": path, "schema": schema}]})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert len(reasons) == 1
    assert error.type == "package-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note.count('schema.json" is not safe')


def test_package_resource_unsafe_schema_trusted():
    path = "data/table.csv"
    schema = "data/../data/schema.json"
    with system.use_context(trusted=True):
        Package({"resources": [{"path": path, "schema": schema}]})


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_package_resource_from_path_error_unsafe():
    resource = "data/../resource.json"
    with pytest.raises(FrictionlessException) as excinfo:
        Package({"resources": [resource]})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert len(reasons) == 1
    assert error.type == "package-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "package-error"
    assert reasons[0].note.count('resource.json" is not safe')


@pytest.mark.vcr
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_package_external_profile_invalid_local_from_descriptor_unsafe():
    profile = "data/../data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        Package({"resources": [resource.to_descriptor()], "profile": profile})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert len(reasons) == 1
    assert error.type == "package-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "package-error"
    assert reasons[0].note.count('camtrap.json" is not safe')


@pytest.mark.vcr
def test_package_external_profile_invalid_local_from_descriptor_unsafe_trusted():
    profile = "data/../data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    with system.use_context(trusted=True):
        package = Package(resources=[resource], profiles=[profile])
        report = package.validate()
        assert report.stats.errors == 5
