from frictionless import Package, steps


# General


def test_step_resource_transform():
    source = Package("data/package/datapackage.json")
    target = source.transform(
        steps=[
            steps.resource_update(name="data", title="It's our data"),
            steps.resource_remove(name="data2"),
            steps.resource_add(name="data2", path="data2.csv"),
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
    assert target.resource_names == ["data", "data2"]
    assert target.get_resource("data").read_rows() == [
        {"id": "A3001", "name": "Taxes", "description": "Zeroed", "amount": 0},
        {"id": "A5032", "name": "Parking Fees", "description": "Zeroed", "amount": 0},
    ]
    assert target.get_resource("data2").read_rows() == [
        {"parent": "A3001", "comment": "It works!"},
        {"parent": "A3001", "comment": "It works!"},
        {"parent": "A5032", "comment": "It works!"},
    ]
