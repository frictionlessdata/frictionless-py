import pytest


# General


@pytest.mark.skip
def test_server_project_file_create(api_client):
    session = api_client.post("/project/create").json()["session"]

    # Create
    with open("data/table.csv", "rb") as file:
        files = {"file": ("table.csv", file, "text/csv")}
        response = api_client.post(
            "/project/create-file", files=files, data=dict(session=session)
        )
        assert response.status_code == 200
        assert response.json()["path"] == "table.csv"

    # List
    response = api_client.post("/project/list-files", json=dict(session=session))
    assert response.status_code == 200
    assert response.json()["paths"] == ["table.csv"]
