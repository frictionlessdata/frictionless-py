from frictionless import Resource, steps


# General


def test_step_field_remove():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.field_remove(names=["id"]),
        ],
    )
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
