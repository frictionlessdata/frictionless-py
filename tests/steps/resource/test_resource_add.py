from frictionless import Package, transform, steps


# General


def test_step_resource_add():
    source = Package("data/package/datapackage.json")
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
