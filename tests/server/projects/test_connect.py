import pytest


# General


@pytest.mark.skip
def test_server_project_connect(api_client):
    response = api_client.post("/project/connect")
    assert response.status_code == 200
    assert len(response.json()["session"]) == 22
