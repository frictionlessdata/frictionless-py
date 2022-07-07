import pytest
from frictionless import Resource, transform, steps


# General


@pytest.mark.xfail(reason="Recover steps")
def test_transform_resource():
    target = transform(
        "data/transform.csv",
        steps=[
            steps.table_normalize(),
            steps.table_melt(field_name="id"),
        ],
    )
    assert isinstance(target, Resource)
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
