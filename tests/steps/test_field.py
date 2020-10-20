from frictionless import Resource, transform_resource, steps


# Pick Fields


def test_step_pick_fields():
    source = Resource(path="data/transform.csv")
    target = transform_resource(source, steps=[steps.pick_fields(names=["id", "name"])])
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


# Skip Fields


def test_step_skip_fields():
    source = Resource(path="data/transform.csv")
    target = transform_resource(source, steps=[steps.skip_fields(names=["id"])])
    assert target.schema == {
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


# Move Field


def test_step_move_field():
    source = Resource(path="data/transform.csv")
    target = transform_resource(source, steps=[steps.move_field(name="id", position=3)])
    assert target.schema == {
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
