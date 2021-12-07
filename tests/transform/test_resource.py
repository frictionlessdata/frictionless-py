from frictionless import Resource, transform, steps


# General


def test_transform_resource():
    source = Resource(path="data/transform.csv")
    source.infer()
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_melt(field_name="id"),
        ],
    )
    assert target.schema == {
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


def test_transform_resource_rename_move_field():
    source = Resource(path="data/transform.csv")
    source.infer()
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.field_update(name="name", new_name="country"),
            steps.field_move(name="country", position=3),
        ],
    )
    assert target.schema == {
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
