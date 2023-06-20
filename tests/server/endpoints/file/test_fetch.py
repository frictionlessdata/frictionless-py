from pathlib import Path

import pytest

from frictionless.server import models

from ...fixtures import folder1, not_secure, url1, url1bytes, url1name

# Action


@pytest.mark.vcr
def test_server_file_fetch(client):
    client("/file/fetch", url=url1)
    assert client("/file/read", path=url1name).bytes == url1bytes
    assert client("/file/list").files == [
        models.File(path=url1name, type="file"),
    ]


@pytest.mark.vcr
def test_server_file_fetch_to_folder(client):
    client("/folder/create", path=folder1)
    path = client("/file/fetch", url=url1, folder=folder1).path
    assert path == str(Path(folder1) / url1name)
    assert client("/file/read", path=path).bytes == url1bytes
    assert client("/file/list").files == [
        models.File(path=folder1, type="folder"),
        models.File(path=path, type="file"),
    ]


@pytest.mark.parametrize("path", not_secure)
def test_server_file_fetch_security(client, path):
    with pytest.raises(Exception):
        client("/file/fetch", url=url1, folder=path)
