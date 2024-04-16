from frictionless import Pipeline, steps
from frictionless.resources import TableResource

# General


def test_step_row_split():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_split(field_name="name", pattern="a"),
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
        {"id": 1, "name": "germ", "population": 83},
        {"id": 1, "name": "ny", "population": 83},
        {"id": 2, "name": "fr", "population": 66},
        {"id": 2, "name": "nce", "population": 66},
        {"id": 3, "name": "sp", "population": 47},
        {"id": 3, "name": "in", "population": 47},
    ]
