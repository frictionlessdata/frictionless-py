import json
from frictionless import Project


dir1 = "dir1"
dir2 = "dir2"
name1 = "name1.txt"
name2 = "name2.txt"
bytes1 = b"bytes1"
bytes2 = b"bytes2"
bytes3 = b'{"key": "value"}'


# Read


def test_project_resource_read_bytes(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    assert project.resource_read_bytes(name1) == bytes1


def test_project_resource_read_data(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes3)
    assert project.resource_read_data(name1) == json.loads(bytes3)


def test_project_resource_read_text(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    assert project.resource_read_text(name1) == bytes1.decode("utf-8")
