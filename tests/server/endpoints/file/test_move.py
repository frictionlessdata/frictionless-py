import pytest
from pathlib import Path
from ...fixtures import name1, bytes1, folder1, folder2, not_secure


# Action


def test_server_file_move(client):
    client("/file/create", path=name1, bytes=bytes1)
    client("/folder/create", path=folder1)
    path = client("/file/move", path=name1, folder=folder1).path
    assert path == str(Path(folder1) / name1)
    assert client("/file/read", path=path).bytes == bytes1
    assert client("/file/list").items == [
        {"path": folder1, "type": "folder"},
        {"path": path, "type": "text"},
    ]


def test_server_file_move_folder(client):
    path2 = str(Path(folder2) / folder1 / name1)
    client("/folder/create", path=folder1)
    client("/folder/create", path=folder2)
    client("/file/create", path=name1, bytes=bytes1, folder=folder1)
    path = client("/file/move", path=folder1, folder=folder2).path
    assert path == str(Path(folder2) / folder1)
    assert client("/file/read", path=path2).bytes == bytes1
    assert client("/file/list").items == [
        {"path": folder2, "type": "folder"},
        {"path": str(Path(folder2) / folder1), "type": "folder"},
        {"path": str(Path(folder2) / folder1 / name1), "type": "text"},
    ]


@pytest.mark.parametrize("path", not_secure)
def test_server_file_move_security(client, path):
    client("/file/create", path=name1, bytes=bytes1)
    with pytest.raises(Exception):
        client("/file/move", path=path, folder=folder1)
    with pytest.raises(Exception):
        client("/file/move", path=name1, folder=path)
