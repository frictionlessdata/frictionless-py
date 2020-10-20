from frictionless import Resource, transform_resource, steps


# Remove Field


def test_step_remove_field():
    source = Resource(path="data/transform.csv")
    medium = [steps.remove_field(name="id"), steps.remove_field(name="population")]
    target = transform_resource(source, steps=medium)
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
