import pytest
from frictionless import Project


name1 = "name1.txt"
name2 = "name2.txt"
bytes1 = b"bytes1"
bytes2 = b"bytes2"
bytes3 = b'{"key": "value"}'
folder1 = "folder1"
folder2 = "folder2"
not_secure = ["/path", "../path", "../", "./"]


# Read


def test_project_read_bytes(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, bytes=bytes1)
    assert project.read_bytes(name1) == bytes1
    assert project.list_files() == [
        {"path": name1, "type": "file"},
    ]


@pytest.mark.parametrize("path", not_secure)
def test_project_read_bytes_security(tmpdir, path):
    project = Project(basepath=tmpdir, is_root=True)
    with pytest.raises(Exception):
        project.read_bytes(path)
