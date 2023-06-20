import pytest

from frictionless.server import models

from ...fixtures import bytes1, name1, not_secure

# Action


def test_server_file_read(client):
    client("/file/create", path=name1, bytes=bytes1)
    assert client("/file/read", path=name1).bytes == bytes1
    assert client("/file/list").files == [
        models.File(path=name1, type="file"),
    ]


@pytest.mark.parametrize("path", not_secure)
def test_server_file_read_security(client, path):
    with pytest.raises(Exception):
        client("/file/read", path=path)
