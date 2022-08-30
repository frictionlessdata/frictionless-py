from fastapi.testclient import TestClient
from frictionless import Resource
from frictionless.server import server


client = TestClient(server)


def test_server_validate():
    resource = Resource(path="data/table.csv")
    response = client.post("/validate", json={"resource": resource.to_descriptor()})
    assert response.status_code == 200
    assert response.json()["report"]["valid"] is True
