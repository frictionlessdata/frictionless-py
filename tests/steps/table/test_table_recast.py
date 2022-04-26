from frictionless import Resource, transform, steps


# General


def test_step_table_recast():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_melt(field_name="id"),
            steps.table_recast(field_name="id"),
        ],
    )
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
