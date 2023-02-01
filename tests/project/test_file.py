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


def test_project_file_copy(tmpdir):
    name1copy = "name1 (copy1).txt"
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    path = project.file_copy(name1)
    assert path == name1copy
    assert project.file_read(name1) == bytes1
    assert project.file_read(name1copy) == bytes1
    assert project.file_list() == [
        {"path": name1copy, "type": "file"},
        {"path": name1, "type": "file"},
    ]


def test_project_file_copy_to_folder(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_create_folder(folder1)
    path = project.file_copy(name1, folder=folder1)
    assert path == str(Path(folder1) / name1)
    assert project.file_read(name1) == bytes1
    assert project.file_read(path) == bytes1
    assert project.file_list() == [
        {"path": folder1, "type": "folder"},
        {"path": path, "type": "file"},
        {"path": name1, "type": "file"},
    ]


def test_project_file_copy_from_folder_to_folder(tmpdir):
    path1 = str(Path(folder1) / name1)
    path2 = str(Path(folder2) / folder1 / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create_folder(folder1)
    project.file_create_folder(folder2)
    project.file_create(name1, bytes=bytes1, folder=folder1)
    path = project.file_copy(folder1, folder=folder2)
    assert path == str(Path(folder2) / folder1)
    assert helpers.read_file(tmpdir / path1, "rb") == bytes1
    assert helpers.read_file(tmpdir / path2, "rb") == bytes1
    assert project.file_list() == [
        {"path": folder1, "type": "folder"},
        {"path": path1, "type": "file"},
        {"path": folder2, "type": "folder"},
        {"path": str(Path(folder2) / folder1), "type": "folder"},
        {"path": str(Path(folder2) / folder1 / name1), "type": "file"},
    ]


# Create


def test_project_file_create(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    path = project.file_create(name1, bytes=bytes1)
    assert helpers.read_file(tmpdir / name1, "rb") == bytes1
    assert path == name1
    assert project.file_list() == [
        {"path": name1, "type": "file"},
    ]


def test_project_file_create_in_folder(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create_folder(folder1)
    path = project.file_create(name1, bytes=bytes1, folder=folder1)
    assert path == str(Path(folder1) / name1)
    assert helpers.read_file(tmpdir / path, "rb") == bytes1
    assert project.file_list() == [
        {"path": folder1, "type": "folder"},
        {"path": path, "type": "file"},
    ]


# Create folder


def test_project_file_create_folder(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    path = project.file_create_folder(folder1)
    assert path == folder1
    assert project.file_list() == [
        {"path": folder1, "type": "folder"},
    ]


# Delete


def test_project_file_delete(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_create(name2, bytes=bytes2)
    project.file_delete(name2)
    assert project.file_list() == [
        {"path": name1, "type": "file"},
    ]


def test_project_file_delete_folder(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create_folder(folder1)
    project.file_create(name1, bytes=bytes1, folder=folder1)
    project.file_delete(folder1)
    assert project.file_list() == []


# List


def test_project_file_list(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_create(name2, bytes=bytes2)
    assert project.file_list() == [
        {"path": name1, "type": "file"},
        {"path": name2, "type": "file"},
    ]


def test_project_file_list_with_folders(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_create_folder(folder1)
    assert project.file_list() == [
        {"path": folder1, "type": "folder"},
        {"path": name1, "type": "file"},
    ]


# List plain


def test_project_file_list_plain(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_create_folder(folder1)
    assert project.file_list_plain() == [folder1, name1]
    assert project.file_list_plain(exclude_folders=True) == [name1]


# Move


def test_project_file_move(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_create_folder(folder1)
    path = project.file_move(name1, folder=folder1)
    assert path == str(Path(folder1) / name1)
    assert project.file_read(path) == bytes1
    assert project.file_list() == [
        {"path": folder1, "type": "folder"},
        {"path": path, "type": "file"},
    ]


def test_project_file_move_folder(tmpdir):
    path2 = str(Path(folder2) / folder1 / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create_folder(folder1)
    project.file_create_folder(folder2)
    project.file_create(name1, bytes=bytes1, folder=folder1)
    path = project.file_move(folder1, folder=folder2)
    assert path == str(Path(folder2) / folder1)
    assert helpers.read_file(tmpdir / path2, "rb") == bytes1
    assert project.file_list() == [
        {"path": folder2, "type": "folder"},
        {"path": str(Path(folder2) / folder1), "type": "folder"},
        {"path": str(Path(folder2) / folder1 / name1), "type": "file"},
    ]


# Read


def test_project_file_read(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    assert project.file_read(name1) == bytes1
    assert project.file_list() == [
        {"path": name1, "type": "file"},
    ]
