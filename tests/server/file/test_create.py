# General


def test_server_file_create(api_client):
    with open("data/table.csv", "rb") as file:
        files = {"file": ("table.csv", file, "text/csv")}
        response = api_client.post("/file/create", files=files)
    assert response.status_code == 200
