# General


def test_server_session_create(api_client):
    response = api_client.post("/session/create")
    assert response.status_code == 200
    assert len(response.json()["token"]) == 22
