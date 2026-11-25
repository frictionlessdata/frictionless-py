import sys

import pytest

from frictionless import FrictionlessException, Package, Resource, platform, system

# General

DP_PROFILES = [
    "https://datapackage.org/profiles/1.0/datapackage.json",
    "https://datapackage.org/profiles/2.0/datapackage.json",
]
UNSAFE_METADATA_PATHS = [
    "/outside/image.png",
    r"C:\outside\image.png",
    r"\\server\share\image.png",
    "../outside/image.png",
    "file:///outside/image.png",
    "s3://bucket/image.png",
    "javascript:alert(1)",
    "mailto:user@example.com",
    "unknown://host/image.png",
    "http://[",
]
SAFE_METADATA_PATHS = [
    "assets/image.png",
    "http://example.com/image.png",
    "https://example.com/image.png",
    "ftp://example.com/image.png",
    "ftps://example.com/image.png",
]


def _package_with_metadata_path(field, path):
    descriptor = {"resources": []}
    if field == "image":
        descriptor["image"] = path
    else:
        name = {
            "contributor": "contributors",
            "license": "licenses",
            "source": "sources",
        }[field]
        descriptor[name] = [{"title": field.title(), "path": path}]
    return descriptor


@pytest.mark.parametrize("schema", DP_PROFILES)
@pytest.mark.parametrize("field", ["image", "contributor", "license", "source"])
@pytest.mark.parametrize("path", UNSAFE_METADATA_PATHS)
def test_package_rejects_unsafe_metadata_paths_issue_1591(schema, field, path):
    descriptor = _package_with_metadata_path(field, path)
    descriptor["$schema"] = schema
    errors = list(Package.metadata_validate(descriptor))
    assert [error.note for error in errors] == [f'path "{path}" is not safe']


@pytest.mark.parametrize("schema", DP_PROFILES)
@pytest.mark.parametrize("field", ["image", "contributor", "license", "source"])
@pytest.mark.parametrize("path", SAFE_METADATA_PATHS)
def test_package_accepts_safe_metadata_paths_issue_1591(schema, field, path):
    descriptor = _package_with_metadata_path(field, path)
    descriptor["$schema"] = schema
    assert not list(Package.metadata_validate(descriptor))


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_package_resource_unsafe_schema():
    path = "data/table.csv"
    schema = "data/../data/schema.json"
    with pytest.raises(FrictionlessException) as excinfo:
        Package({"resources": [{"name": "name", "path": path, "schema": schema}]})
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
        Package({"resources": [{"name": "name", "path": path, "schema": schema}]})


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
@pytest.mark.skipif(sys.version_info < (3, 10), reason="pytest-vcr bug in Python3.8/9")
def test_package_external_profile_invalid_local_from_descriptor_unsafe_trusted():
    profile = "data/../data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    with system.use_context(trusted=True):
        package = Package(resources=[resource], profile=profile)
        report = package.validate()
        assert report.stats["errors"] == 5
