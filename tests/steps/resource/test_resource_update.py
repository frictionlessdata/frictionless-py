from frictionless import Package, transform, steps


# General


def test_step_resource_update():
    source = Package("data/package/datapackage.json")
    target = transform(
        source,
        steps=[
            steps.resource_update(name="data", title="New title"),
        ],
    )
    assert target.get_resource("data").title == "New title"


def test_step_resource_update_new_name():
    source = Package("data/package/datapackage.json")
    target = transform(
        source,
        steps=[
            steps.resource_update(name="data", new_name="new-name"),
        ],
    )
    assert target.get_resource("new-name").path == "data.csv"
