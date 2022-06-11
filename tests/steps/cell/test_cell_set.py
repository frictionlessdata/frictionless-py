from frictionless import Resource, Pipeline, steps


# General


def test_step_cell_set():
    source = Resource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.cell_set(field_name="population", value=100),
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
        {"id": 1, "name": "germany", "population": 100},
        {"id": 2, "name": "france", "population": 100},
        {"id": 3, "name": "spain", "population": 100},
    ]
