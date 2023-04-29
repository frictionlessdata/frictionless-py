from ...fixtures import name1, name2, bytes1, bytes2, folder1


# Action


def test_server_file_list(client):
    client("/file/create", path=name1, bytes=bytes1)
    client("/file/create", path=name2, bytes=bytes2)
    assert client("/file/list").items == [
        {"path": name1, "type": "file"},
        {"path": name2, "type": "file"},
    ]


def test_server_file_list_with_folders(client):
    client("/file/create", path=name1, bytes=bytes1)
    client("/folder/create", path=folder1)
    assert client("/file/list").items == [
        {"path": folder1, "type": "folder"},
        {"path": name1, "type": "file"},
    ]
