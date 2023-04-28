import pytest
from ...fixtures import name1, name2, bytes1, bytes2, folder1, not_secure


# Action


def test_server_file_delete(client):
    client("/file/create", path=name1, bytes=bytes1)
    client("/file/create", path=name2, bytes=bytes2)
    path = client("/file/delete", path=name2).path
    assert path == name2
    assert client("/file/list").items == [
        {"path": name1, "type": "text"},
    ]


def test_server_file_delete_folder(client):
    client("/folder/create", path=folder1)
    client("/file/create", path=name1, bytes=bytes1, folder=folder1)
    path = client("/file/delete", path=folder1).path
    assert path == folder1
    assert client("/file/list").items == []


@pytest.mark.parametrize("path", not_secure)
def test_server_file_delete_security(client, path):
    with pytest.raises(Exception):
        client("/file/delete", path=path)
