# General


def test_server_file_create(api_client):
    token = api_client.post("/session/create").json()["token"]

    # Create
    with open("data/table.csv", "rb") as file:
        files = {"file": ("table.csv", file, "text/csv")}
        response = api_client.post(
            "/session/create-file", files=files, data=dict(token=token)
        )
        assert response.status_code == 200
        assert response.json()["path"] == "table.csv"

    # List
    response = api_client.post("/session/list-files", json=dict(token=token))
    assert response.status_code == 200
    assert response.json()["paths"] == ["table.csv"]
