from frictionless.server import Client

name1 = "name1.txt"
bytes1 = b"bytes1"


def test_project_read_file(tmpdir):
    client = Client(tmpdir)
    client.invoke("file/create", name=name1, bytes=bytes1)
    assert client.invoke("file/read", path=name1).bytes == bytes1
    assert client.invoke("file/list").items == [
        {"path": name1, "type": "text"},
    ]
