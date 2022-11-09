from frictionless import Resource, Pipeline, steps


# General


def test_server_resource_transform(api_client_root):
    pipeline = Pipeline(steps=[steps.cell_set(field_name="name", value="new")])
    resource = Resource(path="data/table.csv", pipeline=pipeline)
    response = api_client_root.post(
        "/resource/transform", json={"resource": resource.to_descriptor()}
    )
    assert response.status_code == 200
    assert response.json()["table"]["rows"] == [
        {"id": 1, "name": "new"},
        {"id": 2, "name": "new"},
    ]
