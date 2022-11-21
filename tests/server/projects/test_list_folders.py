import pytest


# General


@pytest.mark.skip
def test_server_project_list_folders(api_client):
    session = api_client.post("/project/create").json()["session"]

    # Create Dir
    response = api_client.post(
        "/project/create-directory", data=dict(session=session, directoryname="test")
    )

    # List Dir
    response = api_client.post("/project/list-folders", json=dict(session=session))
    assert response.status_code == 200
    assert response.json()["paths"] == ["test"]
