from fastapi.testclient import TestClient
from frictionless.server import server


client = TestClient(server)


def test_server_file_create():
    with open("data/table.csv", "rb") as file:
        files = {"file": ("table.csv", file, "text/csv")}
        response = client.post("/file/create", files=files)
    assert response.status_code == 202
