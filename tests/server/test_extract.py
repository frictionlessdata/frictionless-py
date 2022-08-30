from fastapi.testclient import TestClient
from frictionless import Resource
from frictionless.server import server


client = TestClient(server)


def test_server_extract():
    resource = Resource(path="data/table.csv")
    response = client.post("/extract", json={"resource": resource.to_descriptor()})
    assert response.status_code == 200
    assert response.json()["rows"] == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
