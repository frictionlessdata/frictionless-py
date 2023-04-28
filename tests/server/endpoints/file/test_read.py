import pytest
from frictionless.server import Client

name1 = "name1.txt"
bytes1 = b"bytes1"
not_secure = ["/path", "../path", "../", "./"]


def test_project_read_file(tmpdir):
    client = Client(tmpdir)
    client.invoke("file/create", name=name1, bytes=bytes1)
    assert client.invoke("file/read", path=name1).bytes == bytes1
    assert client.invoke("file/list").items == [
        {"path": name1, "type": "text"},
    ]


@pytest.mark.parametrize("path", not_secure)
def test_project_read_file_security(tmpdir, path):
    client = Client(tmpdir)
    with pytest.raises(Exception):
        client.invoke("file/read", path=path)
