import pytest
from pathlib import Path
from ...fixtures import name1, name2, bytes1, folder1, folder2, not_secure


# Action


def test_server_file_rename(client):
    client("/file/create", path=name1, bytes=bytes1)
    client("/file/rename", path=name1, name=name2)
    assert client("/file/read", path=name2).bytes == bytes1
    assert client("/file/list").items == [
        {"path": name2, "type": "text"},
    ]


def test_server_file_rename_folder(client):
    client("/folder/create", path=folder1)
    client("/file/create", path=name1, bytes=bytes1, folder=folder1)
    client("/file/rename", path=folder1, name=folder2)
    assert client("/file/list").items == [
        {"path": folder2, "type": "folder"},
        {"path": str(Path(folder2) / name1), "type": "text"},
    ]


@pytest.mark.parametrize("path", not_secure)
def test_server_file_rename_security(client, path):
    client("/file/create", path=name1, bytes=bytes1)
    with pytest.raises(Exception):
        client("/file/rename", path=path, name=name2)
    with pytest.raises(Exception):
        client("/file/rename", path=name1, name=path)
