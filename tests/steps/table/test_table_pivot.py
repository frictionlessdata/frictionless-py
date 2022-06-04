from frictionless import Resource, steps


# General


def test_step_table_pivot():
    source = Resource("data/transform-pivot.csv")
    target = source.transform(
        steps=[
            steps.table_normalize(),
            steps.table_pivot(f1="region", f2="gender", f3="units", aggfun=sum),
        ],
    )
    assert target.schema == {
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
