import pytest
from frictionless import Project


name1 = "name1.txt"
name2 = "name2.txt"
name3 = "name3.json"
bytes1 = b"bytes1"
bytes2 = b"bytes2"
bytes3 = b'{"key": "value"}'
folder1 = "folder1"
folder2 = "folder2"
not_secure = ["/path", "../path", "../", "./"]


# Read


def test_project_read_data(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name3, bytes=bytes3)
    assert project.read_data(name3) == {"key": "value"}
    assert project.list_files() == [
        {"path": name3, "type": "file"},
    ]


@pytest.mark.parametrize("path", not_secure)
def test_project_read_data_security(tmpdir, path):
    project = Project(basepath=tmpdir, is_root=True)
    with pytest.raises(Exception):
        project.read_data(path)
