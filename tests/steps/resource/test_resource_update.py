from frictionless import Package, Pipeline, steps, Resource


# General


def test_step_resource_update():
    source = Package("data/package/datapackage.json")
    pipeline = Pipeline(
        steps=[
            steps.resource_update(name="data", descriptor={"title": "New title"}),
        ],
    )
    target = source.transform(pipeline)
    assert target.get_resource("data").title == "New title"


def test_step_resource_update_new_name():
    source = Package("data/package/datapackage.json")
    pipeline = Pipeline(
        steps=[
            steps.resource_update(name="data", descriptor={"name": "new-name"}),
        ],
    )
    target = source.transform(pipeline)
    assert target.get_resource("new-name").path == "data.csv"


def test_step_resource_update_standalone_issue_1351():
    source = Resource("data/resource.json")
    pipeline = Pipeline(
        steps=[
            steps.resource_update(descriptor={"title": "New title"}),
        ],
    )
    target = source.transform(pipeline)
    assert target.title == "New title"
