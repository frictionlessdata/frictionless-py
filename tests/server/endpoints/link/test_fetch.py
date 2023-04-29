import pytest
from ...fixtures import url1, url1name, url1bytes, not_secure


# Action


def test_server_link_fetch(client):
    client("/link/fetch", url=url1)
    assert client("/file/read", path=url1name).bytes == url1bytes
    assert client("/file/list").items == [
        {"path": url1name, "type": "file"},
    ]


@pytest.mark.parametrize("path", not_secure)
def test_server_link_fetch_security(client, path):
    with pytest.raises(Exception):
        client("/link/fetch", url=url1, folder=path)
