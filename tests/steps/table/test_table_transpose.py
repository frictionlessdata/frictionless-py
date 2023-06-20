from frictionless import Pipeline, steps
from frictionless.resources import TableResource

# General


def test_step_table_transpose():
    source = TableResource(path="data/transpose.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_transpose(),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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
