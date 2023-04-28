import pytest
from pathlib import Path
from frictionless import helpers
from ...fixtures import name1, bytes1, folder1, not_secure


# Action


def test_server_file_create(client):
    path = client("/file/create", path=name1, bytes=bytes1).path
    assert helpers.read_file(client.project.public / name1, "rb") == bytes1
    assert path == name1
    assert client("/file/list").items == [
        {"path": name1, "type": "text"},
    ]


def test_server_file_create_in_folder(client):
    client("/folder/create", path=folder1)
    path = client("/file/create", path=name1, bytes=bytes1, folder=folder1).path
    assert path == str(Path(folder1) / name1)
    assert helpers.read_file(client.project.public / path, "rb") == bytes1
    assert client("/file/list").items == [
        {"path": folder1, "type": "folder"},
        {"path": path, "type": "text"},
    ]


@pytest.mark.parametrize("path", not_secure)
def test_server_file_create_security(client, path):
    with pytest.raises(Exception):
        client("/file/create", path=path, bytes=bytes1)
    with pytest.raises(Exception):
        client("/file/create", name=name1, bytes=bytes1, folder=path)
