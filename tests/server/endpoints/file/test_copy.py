import pytest
from pathlib import Path
from ...fixtures import name1, name2, bytes1, folder1, folder2, not_secure


# Action


def test_server_file_copy(client):
    client("/file/create", path=name1, bytes=bytes1)
    path = client("/file/copy", source=name1, target=name2).path
    assert path == name2
    assert client("/file/read", path=name1).bytes == bytes1
    assert client("/file/read", path=name2).bytes == bytes1
    assert client("/file/list").items == [
        {"path": name1, "type": "file"},
        {"path": name2, "type": "file"},
    ]


def test_server_file_copy_deduplicate(client):
    name1copy = "name1 (copy1).txt"
    client("/file/create", path=name1, bytes=bytes1)
    path = client("/file/copy", source=name1, deduplicate=True).path
    assert path == name1copy
    assert client("/file/read", path=name1).bytes == bytes1
    assert client("/file/read", path=name1copy).bytes == bytes1
    assert client("/file/list").items == [
        {"path": name1copy, "type": "file"},
        {"path": name1, "type": "file"},
    ]


def test_server_file_copy_to_folder(client):
    client("/file/create", path=name1, bytes=bytes1)
    client("/folder/create", path=folder1)
    path = client("/file/copy", source=name1, target=folder1).path
    assert path == str(Path(folder1) / name1)
    assert client("/file/read", path=name1).bytes == bytes1
    assert client("/file/read", path=path).bytes == bytes1
    assert client("/file/list").items == [
        {"path": folder1, "type": "folder"},
        {"path": path, "type": "file"},
        {"path": name1, "type": "file"},
    ]


def test_server_file_copy_from_folder_to_folder(client):
    path1 = str(Path(folder1) / name1)
    path2 = str(Path(folder2) / folder1 / name1)
    client("/folder/create", path=folder1)
    client("/folder/create", path=folder2)
    client("/file/create", path=name1, bytes=bytes1, folder=folder1)
    path = client("/file/copy", source=folder1, target=folder2).path
    assert path == str(Path(folder2) / folder1)
    assert client("/file/read", path=path1).bytes == bytes1
    assert client("/file/read", path=path2).bytes == bytes1
    assert client("/file/list").items == [
        {"path": folder1, "type": "folder"},
        {"path": path1, "type": "file"},
        {"path": folder2, "type": "folder"},
        {"path": str(Path(folder2) / folder1), "type": "folder"},
        {"path": str(Path(folder2) / folder1 / name1), "type": "file"},
    ]


@pytest.mark.parametrize("path", not_secure)
def test_server_file_copy_security(client, path):
    client("/file/create", path=name1, bytes=bytes1)
    with pytest.raises(Exception):
        client("/file/copy", path=path)
    with pytest.raises(Exception):
        client("/file/copy", path=name1, target=path)