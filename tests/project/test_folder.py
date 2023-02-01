from pathlib import Path
from frictionless import Project, helpers


name1 = "name1.txt"
name2 = "name2.txt"
bytes1 = b"bytes1"
bytes2 = b"bytes2"
bytes3 = b'{"key": "value"}'
folder1 = "folder1"
folder2 = "folder2"


# Copy


def test_project_folder_copy(tmpdir):
    path1 = str(Path(folder1) / name1)
    path2 = str(Path(folder2) / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.folder_create(folder1)
    project.file_create(name1, bytes=bytes1, folder=folder1)
    path = project.folder_copy(folder1, folder=folder2)
    assert path == folder2
    assert helpers.read_file(tmpdir / path1, "rb") == bytes1
    assert helpers.read_file(tmpdir / path2, "rb") == bytes1
    assert project.file_list() == [
        {"path": folder1, "type": "folder"},
        {"path": path1, "type": "file"},
        {"path": folder2, "type": "folder"},
        {"path": path2, "type": "file"},
    ]


# Create


def test_project_folder_create(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    path = project.folder_create(folder1)
    assert path == folder1
    assert project.file_list() == [
        {"path": folder1, "type": "folder"},
    ]


# Delete


def test_project_file_delete_folder(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.folder_create(folder1)
    project.file_create(name1, bytes=bytes1, folder=folder1)
    project.folder_delete(folder1)
    assert project.file_list() == []


# Move


def test_project_folder_move(tmpdir):
    path2 = str(Path(folder2) / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.folder_create(folder1)
    project.file_create(name1, bytes=bytes1, folder=folder1)
    project.folder_move(folder1, folder=folder2)
    assert helpers.read_file(tmpdir / path2, "rb") == bytes1
    assert project.file_list() == [
        {"path": folder2, "type": "folder"},
        {"path": path2, "type": "file"},
    ]
