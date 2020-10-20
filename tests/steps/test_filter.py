from frictionless import Resource, transform_resource, steps


def test_step_head():
    source = Resource(path="data/transform.csv")
    target = transform_resource(
        source,
        steps=[
            steps.head(limit=2),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_tail():
    source = Resource(path="data/transform.csv")
    target = transform_resource(
        source,
        steps=[
            steps.tail(limit=2),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]
