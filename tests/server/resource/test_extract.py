from frictionless import Resource


# General


def test_server_resource_extract(api_client):
    resource = Resource(path="data/table.csv")
    response = api_client.post(
        "/resource/extract", json={"resource": resource.to_descriptor()}
    )
    assert response.status_code == 200
    assert response.json()["rows"] == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
