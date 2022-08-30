from fastapi.testclient import TestClient
from frictionless.server import server


client = TestClient(server)


def test_server_describe():
    response = client.post("/session/create")
    assert response.status_code == 200
    assert len(response.json()["token"]) == 22
