import pytest

from frictionless.server import models

from ...fixtures import folder1, not_secure

# Create


def test_server_folder_create(client):
    path = client("/folder/create", path=folder1).path
    assert path == folder1
    assert client("/file/list").files == [
        models.File(path=folder1, type="folder"),
    ]


@pytest.mark.parametrize("path", not_secure)
def test_server_folder_create_security(client, path):
    with pytest.raises(Exception):
        client("/folder/create", path=path)
    if path != "./":
        with pytest.raises(Exception):
            client("/folder/create", path=folder1, folder=path)
