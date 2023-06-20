import pytest

from frictionless.server import models

from ...fixtures import name1, not_secure

# Action


@pytest.mark.vcr
def test_server_json_create(client):
    client("/json/create", path=name1, data={"key": "value"})
    assert client("/json/read", path=name1).data == {"key": "value"}
    assert client("/file/list").files == [
        models.File(path=name1, type="file"),
    ]


@pytest.mark.vcr
@pytest.mark.parametrize("path", not_secure)
def test_server_chart_create_security(client, path):
    with pytest.raises(Exception):
        client("/json/create", path=path)
