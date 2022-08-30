# General


def test_server_session_create(api_client):
    response = api_client.post("/session/create")
    assert response.status_code == 200
    assert len(response.json()["token"]) == 22


def test_server_session_create_root(api_client_root):
    response = api_client_root.post("/session/create")
    assert response.status_code == 200
    assert len(response.json()["token"]) == 22
