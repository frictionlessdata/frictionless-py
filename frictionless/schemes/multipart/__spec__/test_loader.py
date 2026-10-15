import json
import sys

import pytest

from frictionless import Dialect, FrictionlessException, platform, schemes
from frictionless.resources import FileResource, TableResource

BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


def test_multipart_loader():
    with TableResource(
        path="data/chunk1.csv", extrapaths=["data/chunk2.csv"]
    ) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_multipart_loader_resource():
    descriptor = {
        "name": "name",
        "path": "chunk1.csv",
        "extrapaths": ["chunk2.csv"],
        "schema": "resource-schema.json",
    }
    with TableResource.from_descriptor(descriptor, basepath="data") as resource:
        assert resource.memory is False
        assert resource.multipart is True
        assert resource.tabular is True
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
@pytest.mark.skipif(sys.version_info < (3, 10), reason="pytest-vcr bug in Python3.8/9")
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_multipart_loader_resource_remote():
    descriptor = {
        "name": "name",
        "path": "chunk2.headless.csv",
        "extrapaths": ["chunk3.csv"],
        "dialect": {"header": False},
        "schema": "schema.json",
    }
    with TableResource.from_descriptor(descriptor, basepath=BASEURL % "data") as resource:
        assert resource.memory is False
        assert resource.multipart is True
        assert resource.tabular is True
        assert resource.read_rows() == [
            {"id": 2, "name": "中国人"},
            {"id": 3, "name": "german"},
        ]


@pytest.mark.vcr
@pytest.mark.skipif(sys.version_info < (3, 10), reason="pytest-vcr bug in Python3.8/9")
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_multipart_loader_resource_remote_both_path_and_basepath():
    descriptor = {
        "name": "name",
        "path": "chunk2.headless.csv",
        "extrapaths": [BASEURL % "data/chunk3.csv"],
        "dialect": {"header": False},
        "schema": "schema.json",
    }
    with TableResource.from_descriptor(descriptor, basepath=BASEURL % "data") as resource:
        assert resource.memory is False
        assert resource.multipart is True
        assert resource.tabular is True
        assert resource.read_rows() == [
            {"id": 2, "name": "中国人"},
            {"id": 3, "name": "german"},
        ]


def test_multipart_loader_resource_error_bad_path():
    resource = TableResource.from_descriptor(
        {
            "name": "name",
            "path": "chunk1.csv",
            "extrapaths": ["chunk2.csv"],
        }
    )
    with pytest.raises(FrictionlessException) as excinfo:
        resource.read_rows()
    error = excinfo.value.error
    assert error.type == "scheme-error"
    assert error.note.count("[Errno 2]") and error.note.count("chunk1.csv")


@pytest.mark.skipif(platform.type == "windows", reason="Stats problem on Windows")
def test_multipart_loader_resource_infer():
    descriptor = {
        "name": "name",
        "path": "data/chunk1.csv",
        "extrapaths": ["data/chunk2.csv"],
    }
    resource = TableResource.from_descriptor(descriptor)
    resource.infer(stats=True)
    assert resource.to_descriptor() == {
        "name": "name",
        "path": "data/chunk1.csv",
        "type": "table",
        "scheme": "multipart",
        "format": "csv",
        "encoding": "utf-8",
        "mediatype": "text/csv",
        "extrapaths": ["data/chunk2.csv"],
        "hash": "sha256:a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8",
        "bytes": 30,
        "fields": 2,
        "rows": 2,
        "schema": {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        },
    }


def test_multipart_loader_resource_validate():
    resource = TableResource.from_descriptor(
        {"name": "name", "path": "data/chunk1.csv", "extrapaths": ["data/chunk2.csv"]}
    )
    report = resource.validate()
    assert report.valid
    assert report.task.stats.get("rows") == 2


# Write


# We're better implement here a round-robin testing including
# reading using TableResource as we do for other tests
@pytest.mark.skip
def test_multipart_loader_resource_write_file(tmpdir):
    target = str(tmpdir.join("table{number}.json"))
    target1 = str(tmpdir.join("table1.json"))
    target2 = str(tmpdir.join("table2.json"))

    # Write
    control = schemes.MultipartControl(chunk_size=80)
    resource = TableResource(data=[["id", "name"], [1, "english"], [2, "german"]])
    resource.write(path=target, scheme="multipart", control=control)

    # Read
    text = ""
    for path in [target1, target2]:
        with open(path) as file:
            text += file.read()
    assert json.loads(text) == [["id", "name"], [1, "english"], [2, "german"]]


# Bugs


def test_multipart_loader_with_compressed_parts_issue_1215():
    with TableResource(
        path="data/chunk1.csv.zip", extrapaths=["data/chunk2.csv.zip"]
    ) as resource:
        assert resource.innerpath is None
        assert resource.compression == "zip"
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_multipart_loader_part_without_trailing_newline_issue_1778(tmpdir):
    # The last row of a part without a trailing newline was glued onto the
    # first row of the next part ({"id": 1, "name": "english2"}).
    path1 = str(tmpdir.join("chunk1.csv"))
    path2 = str(tmpdir.join("chunk2.csv"))
    with open(path1, "wb") as file:
        file.write(b"id,name\n1,english")
    with open(path2, "wb") as file:
        file.write(b"id,name\n2,german\n")
    with TableResource(path=path1, extrapaths=[path2]) as resource:
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "german"},
        ]


def test_multipart_loader_headless_part_without_trailing_newline_issue_1778(tmpdir):
    path1 = str(tmpdir.join("chunk1.csv"))
    path2 = str(tmpdir.join("chunk2.csv"))
    with open(path1, "wb") as file:
        file.write(b"1,english")
    with open(path2, "wb") as file:
        file.write(b"2,german\n")
    resource = TableResource(
        path=path1, extrapaths=[path2], dialect=Dialect(header=False)
    )
    with resource:
        assert resource.read_rows() == [
            {"field1": 1, "field2": "english"},
            {"field1": 2, "field2": "german"},
        ]


def test_multipart_loader_binary_parts_stay_verbatim_issue_1778(tmpdir):
    # Non-tabular parts are chunks of one file: no newline may be inserted.
    path1 = str(tmpdir.join("part1.bin"))
    path2 = str(tmpdir.join("part2.bin"))
    with open(path1, "wb") as file:
        file.write(b"\x00\x01NOEOL")
    with open(path2, "wb") as file:
        file.write(b"\x02\x03\n")
    with FileResource(path=path1, extrapaths=[path2]) as resource:
        assert resource.read_file() == b"\x00\x01NOEOL\x02\x03\n"
