import pytest
from ...fixtures import name3, data3, not_secure


# Action


def test_server_json_write(client):
    client("/json/write", path=name3, data=data3)
    assert client("/json/read", path=name3).data == data3


@pytest.mark.parametrize("path", not_secure)
def test_server_json_read_security(client, path):
    with pytest.raises(Exception):
        client("/json/write", path=path, data=data3)
