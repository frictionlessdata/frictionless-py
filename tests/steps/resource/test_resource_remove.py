from frictionless import Package, transform, steps


# General


def test_step_resource_remove():
    source = Package("data/package/datapackage.json")
    target = source.transform(
        steps=[
            steps.resource_remove(name="data2"),
        ],
    )
    assert target.resource_names == ["data"]
