from ...fixtures import name1, name2, bytes1, bytes2, folder1


# Action


def test_project_list_files(client):
    client("/file/create", path=name1, bytes=bytes1)
    client("/file/create", path=name2, bytes=bytes2)
    assert client("/file/list").items == [
        {"path": name1, "type": "text"},
        {"path": name2, "type": "text"},
    ]


def test_project_list_files_with_folders(client):
    client("/file/create", path=name1, bytes=bytes1)
    client("/folder/create", path=folder1)
    assert client("/file/list").items == [
        {"path": folder1, "type": "folder"},
        {"path": name1, "type": "text"},
    ]
