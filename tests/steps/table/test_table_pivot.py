import pytest
from frictionless import Pipeline, steps
from frictionless.resources import TableResource


# General


@pytest.mark.skip(reason="issue-1220")
def test_step_table_pivot():
    source = TableResource("data/transform-pivot.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_pivot(f1="region", f2="gender", f3="units", aggfun=sum),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "region", "type": "string"},
            {"name": "boy", "type": "integer"},
            {"name": "girl", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"region": "east", "boy": 33, "girl": 29},
        {"region": "west", "boy": 35, "girl": 23},
    ]
