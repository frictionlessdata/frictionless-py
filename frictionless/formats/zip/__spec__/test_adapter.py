import os
import zipfile

import pytest

from frictionless import FrictionlessException, Package, Resource, formats, platform
from frictionless.resources import PackageResource

BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


def test_zip_adapter_to_zip(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    source = Package("data/package.json")
    source.publish(path)
    target = Package(path)
    assert target.name == "name"
    assert target.get_table_resource("name").name == "name"
    assert target.get_table_resource("name").path == "table.csv"
    assert target.get_table_resource("name").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_zip_adapter_to_zip_resource_path(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    source = Package(resources=[Resource(path="data/table.csv")])
    source.publish(path)
    target = Package(path)
    assert target.get_table_resource("table").path == "data/table.csv"
    assert target.get_table_resource("table").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_zip_adapter_to_zip_resource_remote_path(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    source = Package(resources=[Resource(path=BASEURL % "data/table.csv")])
    source.publish(path)
    target = Package(path)
    assert target.get_table_resource("table").path == BASEURL % "data/table.csv"
    assert target.get_table_resource("table").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_zip_adapter_to_zip_resource_memory_inline(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    data = [["id", "name"], [1, "english"], [2, "中国人"]]
    source = Package(resources=[Resource(name="table", data=data)])
    source.publish(path)
    target = Package(path)
    assert target.get_table_resource("table").data == data
    assert target.get_table_resource("table").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_zip_adapter_to_zip_resource_memory_function(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    data = lambda: [["id", "name"], [1, "english"], [2, "中国人"]]
    source = Package(resources=[Resource(name="table", data=data)])
    source.publish(path)
    target = Package(path)
    assert target.get_table_resource("table").path == "table.csv"
    assert target.get_table_resource("table").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_zip_adapter_to_zip_resource_multipart(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    resource = Resource(path="data/chunk1.csv", extrapaths=["data/chunk2.csv"])
    source = Package(resources=[resource])
    source.publish(path)
    target = Package(path)
    assert target.get_table_resource("chunk").path == "data/chunk1.csv"
    assert target.get_table_resource("chunk").extrapaths == ["data/chunk2.csv"]
    assert target.get_table_resource("chunk").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_zip_adapter_to_zip_resource_sql(tmpdir, sqlite_url_data):
    path = os.path.join(tmpdir, "package.zip")
    control = formats.SqlControl(table="table")
    source = Package(resources=[Resource(sqlite_url_data, name="table", control=control)])
    source.publish(path)
    target = Package(path)
    assert target.get_table_resource("table").path == sqlite_url_data
    assert target.get_table_resource("table").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_zip_adapter_from_zip():
    package = Package("data/package.zip")
    assert package.name == "testing"
    assert len(package.resources) == 2
    assert package.get_table_resource("data2").read_rows() == [
        {"parent": "A3001", "comment": "comment1"},
        {"parent": "A3001", "comment": "comment2"},
        {"parent": "A5032", "comment": "comment3"},
    ]


@pytest.mark.vcr
def test_zip_adapter_from_zip_remote():
    package = Package(BASEURL % "data/package.zip")
    assert package.name == "testing"
    assert len(package.resources) == 2
    assert package.get_table_resource("data2").read_rows() == [
        {"parent": "A3001", "comment": "comment1"},
        {"parent": "A3001", "comment": "comment2"},
        {"parent": "A5032", "comment": "comment3"},
    ]


def test_zip_adapter_from_zip_no_descriptor(tmpdir):
    descriptor = str(tmpdir.join("package.zip"))
    with zipfile.ZipFile(descriptor, "w") as zip:
        zip.writestr("data.txt", "foobar")
    with pytest.raises(FrictionlessException) as excinfo:
        Package(descriptor)
    error = excinfo.value.error
    assert error.type == "package-error"
    assert error.note.count("datapackage.json")


def test_zip_adapter_from_zip_innerpath():
    control = formats.zip.ZipControl(innerpath="datapackage.yaml")
    package = Package("data/innerpath.package.zip", control=control)
    assert package.name == "emissions"
    assert len(package.resources) == 10


@pytest.mark.skip
def test_zip_adapter_from_zip_innerpath_yaml():
    # for issue1174
    package = Package("data/innerpath.package.zip")
    assert package.name == "emissions"
    assert len(package.resources) == 10


def test_zip_adapter_validate_package_from_zip():
    package = Package("data/package.zip")
    report = package.validate()
    assert report.valid


def test_zip_adapter_validate_package_from_zip_invalid():
    package = Package("data/package-invalid.zip")
    report = package.validate()
    assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
        [1, 3, None, "blank-row"],
        [1, 3, None, "primary-key"],
        [2, 4, None, "blank-row"],
    ]


def test_zip_adapter_actions_validate_package_from_zip():
    package = Package("data/package.zip")
    report = package.validate()
    assert report.valid


def test_zip_adapter_actions_validate_package_from_zip_invalid():
    package = Package("data/package-invalid.zip")
    report = package.validate()
    assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
        [1, 3, None, "blank-row"],
        [1, 3, None, "primary-key"],
        [2, 4, None, "blank-row"],
    ]


# Bugs


def test_zip_adapter_package_detection_issue_1499():
    resource = Resource("data/package.zip")
    assert isinstance(resource, PackageResource)
    package = resource.read_metadata()
    assert len(package.resources) == 2
