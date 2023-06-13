import pytest
from pathlib import Path
from frictionless.server import models
from ...fixtures import folder1, url1, url1name, url1bytes, not_secure


# Action


@pytest.mark.vcr
def test_server_link_fetch(client):
    client("/link/fetch", url=url1)
    assert client("/file/read", path=url1name).bytes == url1bytes
    assert client("/file/list").files == [
        models.File(path=url1name, type="file"),
    ]


@pytest.mark.vcr
def test_server_link_fetch_to_folder(client):
    client("/folder/create", path=folder1)
    path = client("/link/fetch", url=url1, folder=folder1).path
    assert path == str(Path(folder1) / url1name)
    assert client("/file/read", path=path).bytes == url1bytes
    assert client("/file/list").files == [
        models.File(path=folder1, type="folder"),
        models.File(path=path, type="file"),
    ]


@pytest.mark.parametrize("path", not_secure)
def test_server_link_fetch_security(client, path):
    with pytest.raises(Exception):
        client("/link/fetch", url=url1, folder=path)
