import pytest
from pathlib import Path
from frictionless import helpers
from frictionless.server import Client
from ... import fixtures as fx


# Action


def test_server_file_create(tmpdir):
    client = Client(tmpdir)
    path = client.invoke("/file/create", name=fx.name1, bytes=fx.bytes1).path
    assert helpers.read_file(tmpdir / fx.name1, "rb") == fx.bytes1
    assert path == fx.name1
    assert client.invoke("/file/list").items == [
        {"path": fx.name1, "type": "text"},
    ]


def test_server_file_create_in_folder(tmpdir):
    client = Client(tmpdir)
    client.invoke("/folder/create", path=fx.folder1)
    path = client.invoke(
        "/file/create",
        name=fx.name1,
        bytes=fx.bytes1,
        folder=fx.folder1,
    ).path
    assert path == str(Path(fx.folder1) / fx.name1)
    assert helpers.read_file(tmpdir / path, "rb") == fx.bytes1
    assert client.invoke("/file/list").items == [
        {"path": fx.folder1, "type": "folder"},
        {"path": path, "type": "text"},
    ]


@pytest.mark.parametrize("path", fx.not_secure)
def test_server_file_create_security(tmpdir, path):
    client = Client(tmpdir)
    with pytest.raises(Exception):
        client.invoke("/file/create", path=path, bytes=fx.bytes1)
    with pytest.raises(Exception):
        client.invoke("/file/create", name=fx.name1, bytes=fx.bytes1, folder=path)
