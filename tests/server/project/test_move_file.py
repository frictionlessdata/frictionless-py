import pytest


# General


@pytest.mark.skip
def test_server_project_move_file(api_client):
    session = api_client.post("/project/create").json()["session"]

    # Create File
    with open("data/table.csv", "rb") as file:
        files = {"file": ("table.csv", file, "text/csv")}
        response = api_client.post(
            "/project/create-file", files=files, data=dict(session=session)
        )

    # Create Dir
    response = api_client.post(
        "/project/create-directory", data=dict(session=session, directoryname="folder")
    )

    response = api_client.post(
        "/project/move-file", data=dict(session=session, directoryname="folder")
    )
    assert response.status_code == 200
    assert response.json()["path"] == "test"
