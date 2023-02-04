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


# Create


def test_project_create_folder(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    path = project.create_folder(folder1)
    assert path == folder1
    assert project.list_files() == [
        {"path": folder1, "type": "folder"},
    ]


@pytest.mark.parametrize("path", not_secure)
def test_project_create_folder_security(tmpdir, path):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, bytes=bytes1)
    with pytest.raises(Exception):
        project.create_folder(path)
    with pytest.raises(Exception):
        project.create_folder(folder1, folder=path)
