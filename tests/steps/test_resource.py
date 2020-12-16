from frictionless import Package, transform, steps


# Add


def test_step_resource_add():
    source = Package("data/package/datapackage.json")
    source.infer(only_sample=True)
    target = transform(
        source,
        steps=[
            steps.resource_remove(name="data2"),
            steps.resource_add(name="data2", path="data2.csv"),
        ],
    )
    assert target.resource_names == ["data", "data2"]
    assert target.get_resource("data2").read_rows() == [
        {"parent": "A3001", "comment": "comment1"},
        {"parent": "A3001", "comment": "comment2"},
        {"parent": "A5032", "comment": "comment3"},
    ]


# Remove


def test_step_resource_remove():
    source = Package("data/package/datapackage.json")
    source.infer(only_sample=True)
    target = transform(
        source,
        steps=[
            steps.resource_remove(name="data2"),
        ],
    )
    assert target.resource_names == ["data"]


# Transform


def test_step_resource_transform():
    source = Package("data/package/datapackage.json")
    target = transform(
        source,
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


# Update


def test_step_resource_update():
    source = Package("data/package/datapackage.json")
    source.infer(only_sample=True)
    target = transform(
        source,
        steps=[
            steps.resource_update(name="data", title="New title"),
        ],
    )
    assert target.get_resource("data").title == "New title"
