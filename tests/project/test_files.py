import pytest
from pathlib import Path
from frictionless import Project, helpers


dir1 = "dir1"
dir2 = "dir2"
name1 = "name1.txt"
name2 = "name2.txt"
cont1 = b"cont1"
cont2 = b"cont2"


# List files


def test_project_list_files(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, contents=cont1)
    project.create_file(name2, contents=cont2)
    assert project.list_files() == [name1, name2]


# Create file


def test_project_create_file(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    path = project.create_file(name1, contents=cont1)
    assert project.list_files() == [name1]
    assert helpers.read_file(tmpdir / name1, "rb") == cont1
    assert path == tmpdir / name1


def test_project_create_file_in_directory(tmpdir):
    path = str(Path(dir1) / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.create_dir(dir1)
    project.create_file(path, contents=cont1)
    assert project.list_files() == [path]
    assert project.list_files(with_dirs=True) == [dir1, path]
    assert helpers.read_file(tmpdir / path, "rb") == cont1


# Read file


def test_project_read_file(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, contents=cont1)
    assert project.list_files() == [name1]
    assert project.read_file(name1) == cont1


# Move file


def test_project_move_file(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, contents=cont1)
    project.move_file(name1, name2)
    assert project.list_files() == [name2]
    assert project.read_file(name2) == cont1


def test_project_move_file_into_dir(tmpdir):
    path = str(Path(dir1) / name2)
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, contents=cont1)
    project.create_dir(dir1)
    project.move_file(name1, path)
    assert project.list_files() == [path]
    assert project.read_file(path) == cont1


# Copy file


def test_project_copy_file(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, contents=cont1)
    project.copy_file(name1, name2)
    assert project.list_files() == [name1, name2]
    assert project.read_file(name1) == cont1
    assert project.read_file(name2) == cont1


def test_project_copy_file_target_exists(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, contents=cont1)
    project.copy_file(name1)
    assert project.list_files() == ["name1 (copy1).txt", name1]
    assert project.read_file(name1) == cont1
    assert project.read_file("name1 (copy1).txt") == cont1


# Delete file


def test_project_delete_file(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, contents=cont1)
    project.create_file(name2, contents=cont2)
    project.delete_file(name2)
    assert project.list_files() == [name1]
    project.delete_file(name1)
    assert project.list_files() == []


# Create dir


def test_project_create_dir(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    path = project.create_dir(dir1)
    assert project.list_files() == []
    assert project.list_files(with_dirs=True) == [dir1]
    assert path == tmpdir / dir1


# Move dir


@pytest.mark.skip
def test_project_move_dir(tmpdir):
    path = str(Path(dir1) / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.create_dir(dir1)
    project.create_file(path, contents=cont1)
    project.move_dir(dir1, dir2)
    assert project.list_files() == [path]
    assert project.list_files(with_dirs=True) == [dir1, path]
    assert helpers.read_file(tmpdir / path, "rb") == cont1


# Delete dir


def test_project_delete_dir(tmpdir):
    path = str(Path(dir1) / name1)
    project = Project(basepath=tmpdir, is_root=True)
    project.create_dir(dir1)
    project.create_file(path, contents=cont1)
    assert project.list_files() == [path]
    assert project.list_files(with_dirs=True) == [dir1, path]
    project.delete_dir(dir1)
    assert project.list_files(with_dirs=True) == []
