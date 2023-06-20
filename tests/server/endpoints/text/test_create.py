import pytest

from frictionless.server import models

from ...fixtures import name1, not_secure, text1

# Action


def test_server_text_create(client):
    client("/text/create", path=name1, text=text1)
    assert client("/text/read", path=name1).text == text1
    assert client("/file/list").files == [
        models.File(path=name1, type="file"),
    ]


@pytest.mark.parametrize("path", not_secure)
def test_server_text_read_security(client, path):
    with pytest.raises(Exception):
        client("/text/create", path=path, text=text1)
