import os
import json
import pytest
from frictionless import Resource, validate, helpers
from frictionless import FrictionlessException


IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


def test_multipart_loader():
    with Resource(["data/chunk1.csv", "data/chunk2.csv"]) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_multipart_loader_with_compressed_parts():
    with Resource(["data/chunk1.csv.zip", "data/chunk2.csv.zip"]) as resource:
        assert resource.innerpath == ""
        assert resource.compression == ""
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_multipart_loader_resource():
    descriptor = {
        "path": ["chunk1.csv", "chunk2.csv"],
        "schema": "resource-schema.json",
    }
    resource = Resource(descriptor, basepath="data")
    assert resource.memory is False
    assert resource.multipart is True
    assert resource.tabular is True
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_multipart_loader_resource_remote():
    descriptor = {
        "name": "name",
        "path": ["chunk2.headless.csv", "chunk3.csv"],
        "layout": {"header": False},
        "schema": "schema.json",
    }
    resource = Resource(descriptor, basepath=BASEURL % "data")
    assert resource.memory is False
    assert resource.multipart is True
    assert resource.tabular is True
    assert resource.read_rows() == [
        {"id": 2, "name": "中国人"},
        {"id": 3, "name": "german"},
    ]


@pytest.mark.vcr
def test_multipart_loader_resource_remote_both_path_and_basepath():
    descriptor = {
        "name": "name",
        "path": ["chunk2.headless.csv", BASEURL % "data/chunk3.csv"],
        "layout": {"header": False},
        "schema": "schema.json",
    }
    resource = Resource(descriptor, basepath=BASEURL % "data")
    assert resource.memory is False
    assert resource.multipart is True
    assert resource.tabular is True
    assert resource.read_rows() == [
        {"id": 2, "name": "中国人"},
        {"id": 3, "name": "german"},
    ]


def test_multipart_loader_resource_error_bad_path():
    resource = Resource({"name": "name", "path": ["chunk1.csv", "chunk2.csv"]})
    with pytest.raises(FrictionlessException) as excinfo:
        resource.read_rows()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note.count("[Errno 2]") and error.note.count("chunk1.csv")


def test_multipart_loader_resource_error_bad_path_not_safe_absolute():
    bad_path = os.path.abspath("data/chunk1.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "path": [bad_path, "data/chunk2.csv"]})
    error = excinfo.value.error
    assert error.code == "resource-error"
    assert error.note.count("not safe")


def test_multipart_loader_resource_error_bad_path_not_safe_traversing():
    bad_path = os.path.abspath("data/../chunk2.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "path": ["data/chunk1.csv", bad_path]})
    error = excinfo.value.error
    assert error.code == "resource-error"
    assert error.note.count("not safe")


def test_multipart_loader_resource_infer():
    descriptor = {"path": ["data/chunk1.csv", "data/chunk2.csv"]}
    resource = Resource(descriptor)
    resource.infer(stats=True)
    if IS_UNIX:
        assert resource == {
            "path": ["data/chunk1.csv", "data/chunk2.csv"],
            "profile": "tabular-data-resource",
            "name": "chunk",
            "scheme": "multipart",
            "format": "csv",
            "hashing": "md5",
            "encoding": "utf-8",
            "schema": {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "name", "type": "string"},
                ]
            },
            "stats": {
                "hash": "6c2c61dd9b0e9c6876139a449ed87933",
                "bytes": 30,
                "fields": 2,
                "rows": 2,
            },
        }


def test_multipart_loader_resource_validate():
    report = validate({"path": ["data/chunk1.csv", "data/chunk2.csv"]})
    assert report.valid
    assert report.task.resource.stats["rows"] == 2


# We're better implement here a round-robin testing including
# reading using Resource as we do for other tests
def test_multipart_loader_resource_write_file(tmpdir):
    target = str(tmpdir.join("table{number}.json"))
    target1 = str(tmpdir.join("table1.json"))
    target2 = str(tmpdir.join("table2.json"))

    # Write
    resource = Resource(data=[["id", "name"], [1, "english"], [2, "german"]])
    resource.write(path=target, scheme="multipart", control={"chunkSize": 80})

    # Read
    text = ""
    for path in [target1, target2]:
        with open(path) as file:
            text += file.read()
    assert json.loads(text) == [["id", "name"], [1, "english"], [2, "german"]]
