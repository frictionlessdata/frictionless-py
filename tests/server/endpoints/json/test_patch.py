import pytest

from ...fixtures import data3, name3, not_secure

# Action


def test_server_json_patch(client):
    client("/json/create", path=name3, data=data3)
    client("/file/index", path=name3)
    client("/json/patch", path=name3, data={"name": "test"})
    assert client("/json/read", path=name3).data == {"name": "test"}


@pytest.mark.parametrize("path", not_secure)
def test_server_json_read_security(client, path):
    with pytest.raises(Exception):
        client("/json/patch", path=path, data=data3)
