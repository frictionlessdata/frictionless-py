import os
import pytest
from frictionless import Table, Resource, validate
from frictionless import FrictionlessException


BASE_URL = "https://raw.githubusercontent.com/frictionlessdata/datapackage-py/master/%s"


# Table


def test_table_multipart():
    with Table(["data/chunk1.csv", "data/chunk2.csv"]) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_multipart_with_compressed_parts():
    with Table(["data/chunk1.csv.zip", "data/chunk2.csv.zip"]) as table:
        assert table.compression == "no"
        assert table.compression_path == ""
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Resource


def test_resource_source_multipart():
    descriptor = {
        "path": ["chunk1.csv", "chunk2.csv"],
        "schema": "resource-schema.json",
    }
    resource = Resource(descriptor, basepath="data")
    assert resource.inline is False
    assert resource.multipart is True
    assert resource.tabular is True
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.ci
def test_resource_source_multipart_remote():
    descriptor = {
        "name": "name",
        "path": ["chunk2.csv", "chunk3.csv"],
        "dialect": {"header": False},
        "schema": "resource_schema.json",
    }
    resource = Resource(descriptor, basepath=BASE_URL % "data")
    assert resource.inline is False
    assert resource.multipart is True
    assert resource.tabular is True
    assert resource.read_rows() == [
        {"id": 2, "name": "中国人"},
        {"id": 3, "name": "german"},
    ]


@pytest.mark.ci
def test_resource_source_multipart_remote_both_path_and_basepath():
    descriptor = {
        "name": "name",
        "path": ["chunk2.csv", BASE_URL % "data/chunk3.csv"],
        "dialect": {"header": False},
        "schema": "resource_schema.json",
    }
    resource = Resource(descriptor, basepath=BASE_URL % "data")
    assert resource.inline is False
    assert resource.multipart is True
    assert resource.tabular is True
    assert resource.read_rows() == [
        {"id": 2, "name": "中国人"},
        {"id": 3, "name": "german"},
    ]


def test_resource_source_multipart_error_bad_path():
    resource = Resource({"name": "name", "path": ["chunk1.csv", "chunk2.csv"]})
    with pytest.raises(FrictionlessException) as excinfo:
        resource.read_rows()
    error = excinfo.value.error
    assert error.code == "scheme-error"
    assert error.note == "[Errno 2] No such file or directory: 'chunk1.csv'"


def test_resource_source_multipart_error_bad_path_not_safe_absolute():
    bad_path = os.path.abspath("data/chunk1.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "path": [bad_path, "data/chunk2.csv"]})
    error = excinfo.value.error
    assert error.code == "resource-error"
    assert error.note.count("not safe")


def test_resource_source_multipart_error_bad_path_not_safe_traversing():
    bad_path = os.path.abspath("data/../chunk2.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "path": ["data/chunk1.csv", bad_path]})
    error = excinfo.value.error
    assert error.code == "resource-error"
    assert error.note.count("not safe")


def test_resource_source_multipart_infer():
    descriptor = {"path": ["data/chunk1.csv", "data/chunk2.csv"]}
    resource = Resource(descriptor)
    resource.infer()
    assert resource == {
        "path": ["data/chunk1.csv", "data/chunk2.csv"],
        "profile": "tabular-data-resource",
        "name": "chunk1",
        "scheme": "multipart",
        "format": "csv",
        "hashing": "md5",
        "encoding": "utf-8",
        "compression": "no",
        "compressionPath": "",
        "control": {"newline": ""},
        "dialect": {},
        "query": {},
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


# Validate


def test_validate_multipart_resource():
    report = validate({"path": ["data/chunk1.csv", "data/chunk2.csv"]})
    assert report.valid
    assert report.table.stats["rows"] == 2
