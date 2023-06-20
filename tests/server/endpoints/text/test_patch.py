import pytest

from ...fixtures import name1, not_secure, text1

# Action


def test_server_text_patch(client):
    client("/text/create", path=name1, text=text1)
    client("/file/index", path=name1)
    client("/text/patch", path=name1, text="new")
    assert client("/text/read", path=name1).text == "new"


@pytest.mark.parametrize("path", not_secure)
def test_server_text_read_security(client, path):
    with pytest.raises(Exception):
        client("/text/patch", path=path, data=text1)
