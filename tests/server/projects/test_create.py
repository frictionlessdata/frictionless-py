# General


def test_server_project_create(api_client):
    response = api_client.post("/project/create")
    assert response.status_code == 200
    assert len(response.json()["session"]) == 22
