import json
from frictionless import Project


dir1 = "dir1"
dir2 = "dir2"
name1 = "name1.txt"
name2 = "name2.txt"
cont1 = b"cont1"
cont2 = b"cont2"
cont3 = b'{"key": "value"}'


# Read


def test_project_resource_read_bytes(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, contents=cont1)
    assert project.file_list() == [name1]
    assert project.resource_read_bytes(name1) == cont1


def test_project_resource_read_data(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, contents=cont3)
    assert project.file_list() == [name1]
    assert project.resource_read_data(name1) == json.loads(cont3)


def test_project_resource_read_text(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, contents=cont1)
    assert project.file_list() == [name1]
    assert project.resource_read_text(name1) == cont1.decode("utf-8")
