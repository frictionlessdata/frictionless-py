import pytest
from ...fixtures import name1, bytes1, text1, not_secure


# Action


def test_server_text_read(client):
    client("/file/create", path=name1, bytes=bytes1)
    assert client("/text/read", path=name1).text == text1
    assert client("/file/list").items == [
        {"path": name1, "type": "file"},
    ]


@pytest.mark.parametrize("path", not_secure)
def test_server_text_read_security(client, path):
    with pytest.raises(Exception):
        client("/text/read", path=path)
