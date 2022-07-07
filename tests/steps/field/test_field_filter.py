from frictionless import Resource, transform, steps


# General


def test_step_field_filter():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.field_filter(names=["id", "name"]),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany"},
        {"id": 2, "name": "france"},
        {"id": 3, "name": "spain"},
    ]


def test_step_field_filter_changed_field_order():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.field_filter(names=["name", "id"]),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "id", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"name": "germany", "id": 1},
        {"name": "france", "id": 2},
        {"name": "spain", "id": 3},
    ]
