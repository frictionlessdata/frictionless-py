from frictionless import Resource, steps


# General


def test_step_field_update():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.field_update(name="id", type="string", function=str),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": "1", "name": "germany", "population": 83},
        {"id": "2", "name": "france", "population": 66},
        {"id": "3", "name": "spain", "population": 47},
    ]


def test_step_field_update_with_exact_value():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.field_update(name="id", type="string", value="x"),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": "x", "name": "germany", "population": 83},
        {"id": "x", "name": "france", "population": 66},
        {"id": "x", "name": "spain", "population": 47},
    ]


def test_step_field_update_new_name():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.field_update(name="id", new_name="new-name"),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "new-name", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"new-name": 1, "name": "germany", "population": 83},
        {"new-name": 2, "name": "france", "population": 66},
        {"new-name": 3, "name": "spain", "population": 47},
    ]
