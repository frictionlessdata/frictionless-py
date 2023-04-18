import pytest


# General


@pytest.mark.skip
def test_server_project_read_file(api_client_root):
    response = api_client_root.post("/project/read-file", json={"path": "data/table.csv"})
    assert response.status_code == 200
    assert response.json()["text"].startswith("id,name")
