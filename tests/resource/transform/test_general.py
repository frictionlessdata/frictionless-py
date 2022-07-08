import pytest
from frictionless import Resource, Pipeline, steps


# General


@pytest.mark.xfail(reason="Recover steps")
def test_resource_transform():
    source = Resource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_melt(field_name="id"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "variable"},
            {"name": "value"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "variable": "name", "value": "germany"},
        {"id": 1, "variable": "population", "value": 83},
        {"id": 2, "variable": "name", "value": "france"},
        {"id": 2, "variable": "population", "value": 66},
        {"id": 3, "variable": "name", "value": "spain"},
        {"id": 3, "variable": "population", "value": 47},
    ]


def test_resource_transform_cell_set():
    source = Resource("data/transform.csv")
    pipeline = Pipeline.from_descriptor(
        {
            "steps": [
                {"code": "cell-set", "fieldName": "population", "value": 100},
            ],
        }
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
        {"id": 1, "name": "germany", "population": 100},
        {"id": 2, "name": "france", "population": 100},
        {"id": 3, "name": "spain", "population": 100},
    ]
