from frictionless import Resource


# General


def test_server_resource_extract(api_client_root):
    resource = Resource(path="data/table.csv")
    response = api_client_root.post(
        "/resource/extract", json={"resource": resource.to_descriptor()}
    )
    assert response.status_code == 200
    assert response.json()["table"]["rows"] == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
