import pytest
from pathlib import Path
from frictionless.server import models
from ...fixtures import name1, name2, bytes1, folder1, folder2, not_secure


# Action


def test_server_file_move(client):
    client("/file/create", path=name1, bytes=bytes1)
    client("/file/move", path=name1, toPath=name2)
    assert client("/file/read", path=name2).bytes == bytes1
    assert client("/file/list").files == [
        models.File(path=name2, type="file"),
    ]


def test_server_file_move_to_new_name(client):
    client("/folder/create", path=folder1)
    path1 = client("/file/create", path=name1, bytes=bytes1, folder=folder1).path
    path2 = client("/file/move", path=path1, newName=name2).path
    assert client("/file/read", path=path2).bytes == bytes1
    assert client("/file/list").files == [
        models.File(path=folder1, type="folder"),
        models.File(path=str(Path(folder1) / name2), type="file"),
    ]


def test_server_file_move_to_folder(client):
    client("/file/create", path=name1, bytes=bytes1)
    client("/folder/create", path=folder1)
    path = client("/file/move", path=name1, toPath=folder1).path
    assert path == str(Path(folder1) / name1)
    assert client("/file/read", path=path).bytes == bytes1
    assert client("/file/list").files == [
        models.File(path=folder1, type="folder"),
        models.File(path=path, type="file"),
    ]


def test_server_file_move_folder(client):
    client("/folder/create", path=folder1)
    client("/file/create", path=name1, bytes=bytes1, folder=folder1)
    client("/file/move", path=folder1, toPath=folder2)
    assert client("/file/list").files == [
        models.File(path=folder2, type="folder"),
        models.File(path=str(Path(folder2) / name1), type="file"),
    ]


def test_server_file_move_folder_to_folder(client):
    path2 = str(Path(folder2) / folder1 / name1)
    client("/folder/create", path=folder1)
    client("/folder/create", path=folder2)
    client("/file/create", path=name1, bytes=bytes1, folder=folder1)
    path = client("/file/move", path=folder1, toPath=folder2).path
    assert path == str(Path(folder2) / folder1)
    assert client("/file/read", path=path2).bytes == bytes1
    assert client("/file/list").files == [
        models.File(path=folder2, type="folder"),
        models.File(path=str(Path(folder2) / folder1), type="folder"),
        models.File(path=str(Path(folder2) / folder1 / name1), type="file"),
    ]


@pytest.mark.parametrize("path", not_secure)
def test_server_file_move_security(client, path):
    client("/file/create", path=name1, bytes=bytes1)
    with pytest.raises(Exception):
        client("/file/move", path=path, toPath=folder1)
    with pytest.raises(Exception):
        client("/file/move", path=name1, toPath=path)
