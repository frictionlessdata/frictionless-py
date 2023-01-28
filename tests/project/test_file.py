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
    project.file_copy(name1, name2)
    assert project.file_list() == [name1, name2]
    assert project.file_read(name1) == bytes1
    assert project.file_read(name2) == bytes1


def test_project_file_copy_target_exists(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_copy(name1)
    assert project.file_list() == ["name1 (copy1).txt", name1]
    assert project.file_read(name1) == bytes1
    assert project.file_read("name1 (copy1).txt") == bytes1


def test_project_file_copy_dir(tmpdir):
    path1 = str(Path(dir1) / name1)
    path2 = str(Path(dir2) / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create_folder(dir1)
    project.file_create(path1, bytes=bytes1)
    project.file_copy(dir1, dir2)
    assert project.file_list() == [path1, path2]
    assert project.file_list(with_folders=True) == [dir1, path1, dir2, path2]
    assert helpers.read_file(tmpdir / path1, "rb") == bytes1
    assert helpers.read_file(tmpdir / path2, "rb") == bytes1


# Create


def test_project_file_create(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    path = project.file_create(name1, bytes=bytes1)
    assert project.file_list() == [name1]
    assert helpers.read_file(tmpdir / name1, "rb") == bytes1
    assert path == tmpdir / name1


def test_project_file_create_in_folder(tmpdir):
    path = str(Path(dir1) / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create_folder(dir1)
    project.file_create(path, bytes=bytes1)
    assert project.file_list() == [path]
    assert project.file_list(with_folders=True) == [dir1, path]
    assert helpers.read_file(tmpdir / path, "rb") == bytes1


# Create dir


def test_project_create_folder(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    path = project.file_create_folder(dir1)
    assert project.file_list() == []
    assert project.file_list(with_folders=True) == [dir1]
    assert path == tmpdir / dir1


# Delete


def test_project_file_delete(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_create(name2, bytes=bytes2)
    project.file_delete(name2)
    assert project.file_list() == [name1]
    project.file_delete(name1)
    assert project.file_list() == []


def test_project_file_delete_folder(tmpdir):
    path = str(Path(dir1) / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create_folder(dir1)
    project.file_create(path, bytes=bytes1)
    assert project.file_list() == [path]
    assert project.file_list(with_folders=True) == [dir1, path]
    project.file_delete(dir1)
    assert project.file_list(with_folders=True) == []


# List


def test_project_file_list(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_create(name2, bytes=bytes2)
    assert project.file_list() == [name1, name2]


def test_project_file_list_with_folders(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_create_folder(dir1)
    assert project.file_list() == [name1]
    assert project.file_list(with_folders=True) == [dir1, name1]


def test_project_file_list_only_folders(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_create_folder(dir1)
    assert project.file_list() == [name1]
    assert project.file_list(only_folders=True) == [dir1]


# Move


def test_project_file_move(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_move(name1, name2)
    assert project.file_list() == [name2]
    assert project.file_read(name2) == bytes1


def test_project_file_move_into_folder(tmpdir):
    path = str(Path(dir1) / name2)
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    project.file_create_folder(dir1)
    project.file_move(name1, path)
    assert project.file_list() == [path]
    assert project.file_read(path) == bytes1


def test_project_file_move_folder(tmpdir):
    path1 = str(Path(dir1) / name1)
    path2 = str(Path(dir2) / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create_folder(dir1)
    project.file_create(path1, bytes=bytes1)
    project.file_move(dir1, dir2)
    assert project.file_list() == [path2]
    assert project.file_list(with_folders=True) == [dir2, path2]
    assert helpers.read_file(tmpdir / path2, "rb") == bytes1


# Read


def test_project_file_read(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    assert project.file_list() == [name1]
    assert project.file_read(name1) == bytes1
