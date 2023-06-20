import pytest

from frictionless.server import models

from ...fixtures import bytes1, bytes2, name1, name2, not_secure

# Action


def test_server_file_delete(client):
    client("/file/create", path=name1, bytes=bytes1)
    client("/file/create", path=name2, bytes=bytes2)
    path = client("/file/delete", path=name2).path
    assert path == name2
    assert client("/file/list").files == [
        models.File(path=name1, type="file"),
    ]


@pytest.mark.parametrize("path", not_secure)
def test_server_file_delete_security(client, path):
    with pytest.raises(Exception):
        client("/file/delete", path=path)
