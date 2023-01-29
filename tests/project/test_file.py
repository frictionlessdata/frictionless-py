from pathlib import Path
from frictionless import Project, helpers


dir1 = "dir1"
dir2 = "dir2"
name1 = "name1.txt"
name2 = "name2.txt"
bytes1 = b"bytes1"
bytes2 = b"bytes2"
bytes3 = b'{"key": "value"}'


# Copy


def test_project_file_copy(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    path = project.file_copy(name1, name2)
    assert path == name2
    assert project.file_read(name1) == bytes1
    assert project.file_read(name2) == bytes1
    assert project.file_list() == [
        {"path": name1, "isFolder": False},
        {"path": name2, "isFolder": False},
    ]


def test_project_file_copy_target_exists(tmpdir):
    name1copy = "name1 (copy1).txt"
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    path = project.file_copy(name1)
    assert path == name1copy
    assert project.file_read(name1) == bytes1
    assert project.file_read(name1copy) == bytes1
    assert project.file_list() == [
        {"path": name1copy, "isFolder": False},
        {"path": name1, "isFolder": False},
    ]


def test_project_file_copy_dir(tmpdir):
    path1 = str(Path(dir1) / name1)
    path2 = str(Path(dir2) / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create_folder(dir1)
    project.file_create(path1, bytes=bytes1)
    path = project.file_copy(dir1, dir2)
    assert path == dir2
    assert helpers.read_file(tmpdir / path1, "rb") == bytes1
    assert helpers.read_file(tmpdir / path2, "rb") == bytes1
    assert project.file_list() == [
        {"path": dir1, "isFolder": True},
        {"path": path1, "isFolder": False},
        {"path": dir2, "isFolder": True},
        {"path": path2, "isFolder": False},
    ]


# Create


def test_project_file_create(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    path = project.file_create(name1, bytes=bytes1)
    assert helpers.read_file(tmpdir / name1, "rb") == bytes1
    assert path == name1
    assert project.file_list() == [
        {"path": name1, "isFolder": False},
    ]


def test_project_file_create_in_folder(tmpdir):
    path = str(Path(dir1) / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create_folder(dir1)
    project.file_create(path, bytes=bytes1)
    assert helpers.read_file(tmpdir / path, "rb") == bytes1
    assert project.file_list() == [
        {"path": dir1, "isFolder": True},
        {"path": path, "isFolder": False},
    ]


# Create folder


def test_project_create_folder(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    path = project.file_create_folder(dir1)
    assert path == dir1
    assert project.file_list() == [
        {"path": dir1, "isFolder": True},
    ]


# Delete


def test_project_file_delete(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_create(name2, bytes=bytes2)
    project.file_delete(name2)
    assert project.file_list() == [
        {"path": name1, "isFolder": False},
    ]


def test_project_file_delete_folder(tmpdir):
    path = str(Path(dir1) / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create_folder(dir1)
    project.file_create(path, bytes=bytes1)
    project.file_delete(dir1)
    assert project.file_list() == []


# List


def test_project_file_list(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_create(name2, bytes=bytes2)
    assert project.file_list() == [
        {"path": name1, "isFolder": False},
        {"path": name2, "isFolder": False},
    ]


def test_project_file_list_with_folders(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_create_folder(dir1)
    assert project.file_list() == [
        {"path": dir1, "isFolder": True},
        {"path": name1, "isFolder": False},
    ]


# List plain


def test_project_file_list_plain(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_create_folder(dir1)
    assert project.file_list_plain() == [dir1, name1]
    assert project.file_list_plain(exclude_folders=True) == [name1]


# Move


def test_project_file_move(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_move(name1, name2)
    assert project.file_read(name2) == bytes1
    assert project.file_list() == [
        {"path": name2, "isFolder": False},
    ]


def test_project_file_move_into_folder(tmpdir):
    path = str(Path(dir1) / name2)
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_create_folder(dir1)
    project.file_move(name1, path)
    assert project.file_read(path) == bytes1
    assert project.file_list() == [
        {"path": dir1, "isFolder": True},
        {"path": path, "isFolder": False},
    ]


def test_project_file_move_folder(tmpdir):
    path1 = str(Path(dir1) / name1)
    path2 = str(Path(dir2) / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create_folder(dir1)
    project.file_create(path1, bytes=bytes1)
    project.file_move(dir1, dir2)
    assert helpers.read_file(tmpdir / path2, "rb") == bytes1
    assert project.file_list() == [
        {"path": dir2, "isFolder": True},
        {"path": path2, "isFolder": False},
    ]


# Read


def test_project_file_read(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    assert project.file_read(name1) == bytes1
    assert project.file_list() == [
        {"path": name1, "isFolder": False},
    ]
