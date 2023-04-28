import pytest
from frictionless.server import Client
from ... import fixtures as fx


# Action


def test_server_file_read(tmpdir):
    client = Client(tmpdir)
    client.invoke("file/create", name=fx.name1, bytes=fx.bytes1)
    assert client.invoke("file/read", path=fx.name1).bytes == fx.bytes1
    assert client.invoke("file/list").items == [
        {"path": fx.name1, "type": "text"},
    ]


@pytest.mark.parametrize("path", fx.not_secure)
def test_server_file_read_security(tmpdir, path):
    client = Client(tmpdir)
    with pytest.raises(Exception):
        client.invoke("file/read", path=path)
