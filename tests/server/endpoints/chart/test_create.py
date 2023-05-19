import pytest
from frictionless.server import models
from ...fixtures import not_secure


# Action


@pytest.mark.vcr
def test_server_chart_create(client):
    client("/chart/create")
    assert client("/json/read", path="chart.json").data == {"encoding": {}}
    assert client("/file/list").files == [
        models.File(path="chart.json", type="file"),
    ]


@pytest.mark.vcr
def test_server_chart_create_with_path(client):
    client("/chart/create", path="mychart.json")
    assert client("/json/read", path="mychart.json").data == {"encoding": {}}
    assert client("/file/list").files == [
        models.File(path="mychart.json", type="file"),
    ]


@pytest.mark.vcr
@pytest.mark.parametrize("path", not_secure)
def test_server_chart_create_security(client, path):
    with pytest.raises(Exception):
        client("/chart/create", path=path)
