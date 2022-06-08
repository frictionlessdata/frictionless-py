from frictionless import Resource, Pipeline, steps


# General


def test_step_table_transpose():
    source = Resource("data/transpose.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_transpose(),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }

    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]
