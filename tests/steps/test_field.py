from frictionless import Resource, transform_resource, steps


def test_step_remove_field():
    source = Resource(path="data/transform.csv")
    target = transform_resource(
        source,
        steps=[
            steps.remove_field("id"),
            steps.remove_field("capital_id"),
        ],
    )
    # TODO: why missing values are here?
    assert target.schema == {
        "fields": [
            {"missingValues": [""], "name": "name", "type": "string"},
            {"missingValues": [""], "name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"name": "britain", "population": 67},
        {"name": "france", "population": 67},
        {"name": "germany", "population": 83},
        {"name": "italy", "population": 60},
    ]
