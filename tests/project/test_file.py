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


def test_project_copy_file(tmpdir):
    name1copy = "name1 (copy1).txt"
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, bytes=bytes1)
    path = project.copy_file(name1)
    assert path == name1copy
    assert project.read_file(name1) == bytes1
    assert project.read_file(name1copy) == bytes1
    assert project.list_files() == [
        {"path": name1copy, "type": "file"},
        {"path": name1, "type": "file"},
    ]


def test_project_copy_file_to_folder(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, bytes=bytes1)
    project.create_folder(folder1)
    path = project.copy_file(name1, folder=folder1)
    assert path == str(Path(folder1) / name1)
    assert project.read_file(name1) == bytes1
    assert project.read_file(path) == bytes1
    assert project.list_files() == [
        {"path": folder1, "type": "folder"},
        {"path": path, "type": "file"},
        {"path": name1, "type": "file"},
    ]


def test_project_copy_file_from_folder_to_folder(tmpdir):
    path1 = str(Path(folder1) / name1)
    path2 = str(Path(folder2) / folder1 / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.create_folder(folder1)
    project.create_folder(folder2)
    project.create_file(name1, bytes=bytes1, folder=folder1)
    path = project.copy_file(folder1, folder=folder2)
    assert path == str(Path(folder2) / folder1)
    assert helpers.read_file(tmpdir / path1, "rb") == bytes1
    assert helpers.read_file(tmpdir / path2, "rb") == bytes1
    assert project.list_files() == [
        {"path": folder1, "type": "folder"},
        {"path": path1, "type": "file"},
        {"path": folder2, "type": "folder"},
        {"path": str(Path(folder2) / folder1), "type": "folder"},
        {"path": str(Path(folder2) / folder1 / name1), "type": "file"},
    ]


# Create


def test_project_create_file(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    path = project.create_file(name1, bytes=bytes1)
    assert helpers.read_file(tmpdir / name1, "rb") == bytes1
    assert path == name1
    assert project.list_files() == [
        {"path": name1, "type": "file"},
    ]


def test_project_create_file_in_folder(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_folder(folder1)
    path = project.create_file(name1, bytes=bytes1, folder=folder1)
    assert path == str(Path(folder1) / name1)
    assert helpers.read_file(tmpdir / path, "rb") == bytes1
    assert project.list_files() == [
        {"path": folder1, "type": "folder"},
        {"path": path, "type": "file"},
    ]


# Delete


def test_project_delete_file(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, bytes=bytes1)
    project.create_file(name2, bytes=bytes2)
    project.delete_file(name2)
    assert project.list_files() == [
        {"path": name1, "type": "file"},
    ]


def test_project_delete_file_folder(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_folder(folder1)
    project.create_file(name1, bytes=bytes1, folder=folder1)
    project.delete_file(folder1)
    assert project.list_files() == []


# List


def test_project_list_files(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, bytes=bytes1)
    project.create_file(name2, bytes=bytes2)
    assert project.list_files() == [
        {"path": name1, "type": "file"},
        {"path": name2, "type": "file"},
    ]


def test_project_list_files_with_folders(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, bytes=bytes1)
    project.create_folder(folder1)
    assert project.list_files() == [
        {"path": folder1, "type": "folder"},
        {"path": name1, "type": "file"},
    ]


# Move


def test_project_move_file(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, bytes=bytes1)
    project.create_folder(folder1)
    path = project.move_file(name1, folder=folder1)
    print(path)
    assert path == str(Path(folder1) / name1)
    assert project.read_file(path) == bytes1
    assert project.list_files() == [
        {"path": folder1, "type": "folder"},
        {"path": path, "type": "file"},
    ]


def test_project_move_file_folder(tmpdir):
    path2 = str(Path(folder2) / folder1 / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.create_folder(folder1)
    project.create_folder(folder2)
    project.create_file(name1, bytes=bytes1, folder=folder1)
    path = project.move_file(folder1, folder=folder2)
    assert path == str(Path(folder2) / folder1)
    assert helpers.read_file(tmpdir / path2, "rb") == bytes1
    assert project.list_files() == [
        {"path": folder2, "type": "folder"},
        {"path": str(Path(folder2) / folder1), "type": "folder"},
        {"path": str(Path(folder2) / folder1 / name1), "type": "file"},
    ]


# Read


def test_project_read_file(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, bytes=bytes1)
    assert project.read_file(name1) == bytes1
    assert project.list_files() == [
        {"path": name1, "type": "file"},
    ]


# Rename


def test_project_rename_file(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, bytes=bytes1)
    project.rename_file(name1, name=name2)
    assert project.read_file(name2) == bytes1
    assert project.list_files() == [
        {"path": name2, "type": "file"},
    ]


def test_project_rename_file_folder(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_folder(folder1)
    project.create_file(name1, bytes=bytes1, folder=folder1)
    project.rename_file(folder1, name=folder2)
    assert project.list_files() == [
        {"path": folder2, "type": "folder"},
        {"path": str(Path(folder2) / name1), "type": "file"},
    ]
