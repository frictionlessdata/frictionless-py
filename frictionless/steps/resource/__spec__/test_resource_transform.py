from frictionless import Package, Pipeline, steps

# General


def test_step_resource_transform():
    source = Package("data/package/datapackage.json")
    pipeline = Pipeline(
        steps=[
            steps.resource_update(name="data", descriptor={"title": "It's our data"}),
            steps.resource_remove(name="data2"),
            steps.resource_add(name="data2", descriptor={"path": "data2.csv"}),
            steps.resource_transform(
                name="data",
                steps=[
                    steps.cell_set(field_name="description", value="Zeroed"),
                    steps.cell_set(field_name="amount", value=0),
                ],
            ),
            steps.resource_transform(
                name="data2",
                steps=[
                    steps.cell_set(field_name="comment", value="It works!"),
                ],
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.resource_names == ["data", "data2"]
    assert target.get_table_resource("data").read_rows() == [
        {"id": "A3001", "name": "Taxes", "description": "Zeroed", "amount": 0},
        {"id": "A5032", "name": "Parking Fees", "description": "Zeroed", "amount": 0},
    ]
    assert target.get_table_resource("data2").read_rows() == [
        {"parent": "A3001", "comment": "It works!"},
        {"parent": "A3001", "comment": "It works!"},
        {"parent": "A5032", "comment": "It works!"},
    ]
