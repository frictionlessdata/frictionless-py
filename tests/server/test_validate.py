from fastapi.testclient import TestClient
from frictionless import Inquiry, InquiryTask
from frictionless.server import server


client = TestClient(server)


def test_server_validate():
    inquiry = Inquiry(tasks=[InquiryTask(path="data/table.csv")])
    response = client.post("/validate", json={"inquiry": inquiry.to_descriptor()})
    assert response.status_code == 200
    assert response.json()["report"]["valid"] is True
