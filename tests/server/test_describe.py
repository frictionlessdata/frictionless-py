from fastapi.testclient import TestClient
from frictionless.server import server


client = TestClient(server)


def test_server_describe():
    response = client.get("/describe")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
