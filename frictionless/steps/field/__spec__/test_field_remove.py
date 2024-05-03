from frictionless import Pipeline, steps
from frictionless.resources import TableResource

# General


def test_step_field_remove():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_remove(names=["id"]),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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


# Bugs


def test_step_field_remove_missing_label():
    source = TableResource(data=b"field1,\n1,2", format="csv")
    pipeline = Pipeline(
        steps=[
            steps.field_remove(names=["field2"]),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "field1", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"field1": 1},
    ]
