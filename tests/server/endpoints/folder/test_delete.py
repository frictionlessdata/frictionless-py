import pytest

from ...fixtures import bytes1, folder1, name1, not_secure

# Action


def test_server_folder_delete(client):
    client("/folder/create", path=folder1)
    client("/file/create", path=name1, bytes=bytes1, folder=folder1)
    path = client("/folder/delete", path=folder1).path
    assert path == folder1
    assert client("/file/list").files == []


@pytest.mark.parametrize("path", not_secure)
def test_server_file_delete_security(client, path):
    with pytest.raises(Exception):
        client("/folder/delete", path=path)
