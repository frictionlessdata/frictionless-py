from pathlib import Path

import pytest

from frictionless.server import models

from ...fixtures import bytes1, folder1, name1, name2, not_secure

# Action


def test_server_file_copy(client):
    client("/file/create", path=name1, bytes=bytes1)
    path = client("/file/copy", path=name1, toPath=name2).path
    assert path == name2
    assert client("/file/read", path=name1).bytes == bytes1
    assert client("/file/read", path=name2).bytes == bytes1
    assert client("/file/list").files == [
        models.File(path=name1, type="file"),
        models.File(path=name2, type="file"),
    ]


def test_server_file_copy_deduplicate(client):
    name1copy = "name1 (copy1).txt"
    client("/file/create", path=name1, bytes=bytes1)
    path = client("/file/copy", path=name1, deduplicate=True).path
    assert path == name1copy
    assert client("/file/read", path=name1).bytes == bytes1
    assert client("/file/read", path=name1copy).bytes == bytes1
    assert client("/file/list").files == [
        models.File(path=name1copy, type="file"),
        models.File(path=name1, type="file"),
    ]


def test_server_file_copy_to_folder(client):
    client("/file/create", path=name1, bytes=bytes1)
    client("/folder/create", path=folder1)
    path = client("/file/copy", path=name1, toPath=folder1).path
    assert path == str(Path(folder1) / name1)
    assert client("/file/read", path=name1).bytes == bytes1
    assert client("/file/read", path=path).bytes == bytes1
    assert client("/file/list").files == [
        models.File(path=folder1, type="folder"),
        models.File(path=path, type="file"),
        models.File(path=name1, type="file"),
    ]


@pytest.mark.parametrize("path", not_secure)
def test_server_file_copy_security(client, path):
    client("/file/create", path=name1, bytes=bytes1)
    with pytest.raises(Exception):
        client("/file/copy", path=path)
    with pytest.raises(Exception):
        client("/file/copy", path=name1, toPath=path)
