from frictionless import Pipeline, steps
from frictionless.resources import TableResource

# General


def test_step_field_move():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_move(name="id", position=3),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "id", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"name": "germany", "population": 83, "id": 1},
        {"name": "france", "population": 66, "id": 2},
        {"name": "spain", "population": 47, "id": 3},
    ]


# Bugs


def test_transform_rename_move_field_issue_953():
    source = TableResource(
        data=[
            {"id": 1, "name": "germany", "population": 83},
            {"id": 2, "name": "france", "population": 66},
            {"id": 3, "name": "spain", "population": 47},
        ]
    )
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.field_update(name="name", descriptor={"name": "country"}),
            steps.field_move(name="country", position=3),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "population", "type": "integer"},
            {"name": "country", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "population": 83, "country": "germany"},
        {"id": 2, "population": 66, "country": "france"},
        {"id": 3, "population": 47, "country": "spain"},
    ]
