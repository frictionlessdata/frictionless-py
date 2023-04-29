import pytest
from pathlib import Path
from ...fixtures import folder1, url1, url1name, url1bytes, not_secure


# Action


@pytest.mark.vcr
def test_server_link_fetch(client):
    client("/link/fetch", url=url1)
    assert client("/file/read", path=url1name).bytes == url1bytes
    assert client("/file/list").items == [
        {"path": url1name, "type": "file"},
    ]


@pytest.mark.vcr
def test_server_link_fetch_to_folder(client):
    client("/folder/create", path=folder1)
    path = client("/link/fetch", url=url1, folder=folder1).path
    assert path == str(Path(folder1) / url1name)
    assert client("/file/read", path=path).bytes == url1bytes
    assert client("/file/list").items == [
        {"path": folder1, "type": "folder"},
        {"path": path, "type": "file"},
    ]


@pytest.mark.vcr
@pytest.mark.parametrize("path", not_secure)
def test_server_link_fetch_security(client, path):
    with pytest.raises(Exception):
        client("/link/fetch", url=url1, folder=path)
