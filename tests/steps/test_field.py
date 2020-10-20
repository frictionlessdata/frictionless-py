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


# Add Field


def test_step_add_field():
    source = Resource(path="data/transform.csv")
    target = transform_resource(
        source, steps=[steps.add_field(name="note", type="string", value="eu")]
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "eu"},
        {"id": 2, "name": "france", "population": 66, "note": "eu"},
        {"id": 3, "name": "spain", "population": 47, "note": "eu"},
    ]


def test_step_add_field_with_position():
    source = Resource(path="data/transform.csv")
    target = transform_resource(
        source, steps=[steps.add_field(name="note", position=1, value="eu")]
    )
    assert target.schema == {
        "fields": [
            {"name": "note"},
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"note": "eu", "id": 1, "name": "germany", "population": 83},
        {"note": "eu", "id": 2, "name": "france", "population": 66},
        {"note": "eu", "id": 3, "name": "spain", "population": 47},
    ]


def test_step_add_field_with_formula():
    source = Resource(path="data/transform.csv")
    target = transform_resource(
        source,
        steps=[steps.add_field(name="calc", value="<formula>id * 100 + population")],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "calc"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "calc": 183},
        {"id": 2, "name": "france", "population": 66, "calc": 266},
        {"id": 3, "name": "spain", "population": 47, "calc": 347},
    ]


def test_step_add_field_with_value_callable():
    source = Resource(path="data/transform.csv")
    target = transform_resource(
        source,
        steps=[
            steps.add_field(
                name="calc", value=lambda row: row["id"] * 100 + row["population"]
            )
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "calc"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "calc": 183},
        {"id": 2, "name": "france", "population": 66, "calc": 266},
        {"id": 3, "name": "spain", "population": 47, "calc": 347},
    ]


# Add Increment Field


def test_step_add_increment_field():
    source = Resource(path="data/transform.csv")
    target = transform_resource(
        source, steps=[steps.add_increment_field(name="index", start=0)]
    )
    assert target.schema == {
        "fields": [
            {"name": "index", "type": "integer"},
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"index": 0, "id": 1, "name": "germany", "population": 83},
        {"index": 1, "id": 2, "name": "france", "population": 66},
        {"index": 2, "id": 3, "name": "spain", "population": 47},
    ]


# Update Field


def test_step_update_field():
    source = Resource(path="data/transform.csv")
    target = transform_resource(
        source, steps=[steps.update_field(name="id", type="string", value=str)]
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
