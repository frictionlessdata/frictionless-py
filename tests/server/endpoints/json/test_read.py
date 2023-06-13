import pytest
from ...fixtures import name3, bytes3, data3, not_secure


# Action


def test_server_json_read(client):
    client("/file/create", path=name3, bytes=bytes3)
    assert client("/json/read", path=name3).data == data3


@pytest.mark.parametrize("path", not_secure)
def test_server_json_read_security(client, path):
    with pytest.raises(Exception):
        client("/json/read", path=path)
