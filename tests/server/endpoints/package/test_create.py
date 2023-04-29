import pytest
from ...fixtures import not_secure


# Action


@pytest.mark.vcr
def test_server_package_create(client):
    client("/package/create")
    assert client("/json/read", path="datapackage.json").data == {"resources": []}
    assert client("/file/list").items == [
        {"path": "datapackage.json", "type": "file"},
    ]


@pytest.mark.vcr
def test_server_package_create_with_path(client):
    client("/package/create", path="dp.json")
    assert client("/json/read", path="dp.json").data == {"resources": []}
    assert client("/file/list").items == [
        {"path": "dp.json", "type": "file"},
    ]


@pytest.mark.vcr
@pytest.mark.parametrize("path", not_secure)
def test_server_package_create_security(client, path):
    with pytest.raises(Exception):
        client("/package/create", path=path)
