from frictionless import Resource, transform_resource, steps


def test_step_remove_field():
    source = Resource(path="data/transform.csv")
    target = transform_resource(
        source,
        steps=[
            steps.remove_field("id"),
            steps.remove_field("population"),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "name", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"name": "germany"},
        {"name": "france"},
        {"name": "spain"},
    ]
