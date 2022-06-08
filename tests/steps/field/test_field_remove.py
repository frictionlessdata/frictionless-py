from frictionless import Resource, Pipeline, steps


# General


def test_step_field_remove():
    source = Resource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_remove(names=["id"]),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"name": "germany", "population": 83},
        {"name": "france", "population": 66},
        {"name": "spain", "population": 47},
    ]
