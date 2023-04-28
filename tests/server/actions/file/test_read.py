from frictionless.server import Project
from frictionless.server.actions import file

name1 = "name1.txt"
bytes1 = b"bytes1"


def test_project_read_file(tmpdir):
    project = Project(tmpdir)
    file.create.action(project, file.create.Props(name=name1, bytes=bytes1))
    assert file.read.action(project, file.read.Props(path=name1)) == bytes1
    assert file.list.action(project) == [
        {"path": name1, "type": "text"},
    ]


def test_project_read_file_2(tmpdir):
    client = TestClient(tmpdir)
    client("file/create", name=name1, bytes=bytes1)
    assert client("file/read", path=name1) == bytes1
    assert client("file/list") == [
        {"path": name1, "type": "text"},
    ]
