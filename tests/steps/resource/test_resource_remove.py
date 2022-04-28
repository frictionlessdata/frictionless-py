from frictionless import Package, transform, steps


# General


def test_step_resource_remove():
    source = Package("data/package/datapackage.json")
    target = transform(
        source,
        steps=[
            steps.resource_remove(name="data2"),
        ],
    )
    assert target.resource_names == ["data"]
