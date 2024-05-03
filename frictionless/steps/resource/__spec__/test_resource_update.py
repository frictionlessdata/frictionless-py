from frictionless import Package, Pipeline, Schema, steps, transform
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


def test_step_resource_update_referenced_as_foreign_key():
    resource1 = TableResource(name="resource1", path="data/transform.csv")
    resource2 = TableResource(name="resource2")
    resource1.schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
                {"name": "population", "type": "integer"},
            ],
            "primaryKey": ["id"],
        }
    )
    resource2.schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "address", "type": "string"},
                {"name": "country_name", "type": "integer"},
            ],
            "primaryKey": ["id"],
            "foreignKeys": [
                {
                    "fields": ["country_name"],
                    "reference": {"fields": ["id"], "resource": "resource1"},
                }
            ],
        }
    )
    package = Package(name="test-package", resources=[resource1, resource2])
    transform(
        package,
        steps=[
            steps.resource_transform(
                name="resource1",
                steps=[
                    steps.resource_update(
                        name="resource1", descriptor={"name": "first-resource"}
                    )
                ],
            )
        ],
    )
    assert (
        package.get_resource("first-resource").validate().flatten(["title", "message"])
        == []
    )
    assert (
        package.get_resource("resource2").schema.foreign_keys[0]["reference"]["resource"]
        == "first-resource"
    )
