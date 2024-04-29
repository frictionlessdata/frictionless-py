from frictionless import Package, Pipeline, steps

# General


def test_step_resource_remove():
    source = Package("data/package/datapackage.json")
    pipeline = Pipeline(
        steps=[
            steps.resource_remove(name="data2"),
        ],
    )
    target = source.transform(pipeline)
    assert target.resource_names == ["data"]
