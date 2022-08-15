import pytest
import zipfile
from frictionless import Package, FrictionlessException


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


def test_package_compression_implicit_gz():
    package = Package("data/compression/datapackage.json")
    resource = package.get_resource("implicit-gz")
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_package_compression_implicit_zip():
    package = Package("data/compression/datapackage.json")
    resource = package.get_resource("implicit-zip")
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_package_compression_explicit_gz():
    package = Package("data/compression/datapackage.json")
    resource = package.get_resource("explicit-gz")
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_package_compression_explicit_zip():
    package = Package("data/compression/datapackage.json")
    resource = package.get_resource("explicit-zip")
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_package_from_zip():
    package = Package("data/package.zip")
    assert package.name == "testing"
    assert len(package.resources) == 2
    assert package.get_resource("data2").read_rows() == [
        {"parent": "A3001", "comment": "comment1"},
        {"parent": "A3001", "comment": "comment2"},
        {"parent": "A5032", "comment": "comment3"},
    ]


@pytest.mark.vcr
def test_package_from_zip_remote():
    package = Package(BASEURL % "data/package.zip")
    assert package.name == "testing"
    assert len(package.resources) == 2
    assert package.get_resource("data2").read_rows() == [
        {"parent": "A3001", "comment": "comment1"},
        {"parent": "A3001", "comment": "comment2"},
        {"parent": "A5032", "comment": "comment3"},
    ]


def test_package_from_zip_no_descriptor(tmpdir):
    descriptor = str(tmpdir.join("package.zip"))
    with zipfile.ZipFile(descriptor, "w") as zip:
        zip.writestr("data.txt", "foobar")
    with pytest.raises(FrictionlessException) as excinfo:
        Package(descriptor)
    error = excinfo.value.error
    assert error.type == "package-error"
    assert error.note.count("datapackage.json")


def test_package_from_zip_innerpath():
    package = Package("data/innerpath.package.zip", innerpath="datapackage.yaml")
    assert package.name == "emissions"
    assert len(package.resources) == 10


def test_package_from_zip_innerpath_yaml():
    # for issue1174
    package = Package("data/innerpath.package.zip")
    assert package.name == "emissions"
    assert len(package.resources) == 10
