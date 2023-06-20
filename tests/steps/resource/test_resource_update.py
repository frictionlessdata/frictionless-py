from frictionless import Package, Pipeline, steps
from frictionless.resources import TableResource

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


# Bugs


def test_step_resource_update_standalone_issue_1351():
    source = TableResource.from_descriptor("data/resource.json")
    pipeline = Pipeline(
        steps=[
            steps.resource_update(descriptor={"title": "New title"}),
        ],
    )
    target = source.transform(pipeline)
    assert target.title == "New title"
