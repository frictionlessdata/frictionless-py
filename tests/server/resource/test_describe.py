# General


def test_server_resource_describe(api_client_root):
    response = api_client_root.post("/resource/describe", json={"path": "data/table.csv"})
    assert response.status_code == 200
    assert response.json()["resource"] == {
        "name": "table",
        "path": "data/table.csv",
        "type": "table",
        "scheme": "file",
        "format": "csv",
        "encoding": "utf-8",
        "mediatype": "text/csv",
        "schema": {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        },
    }
