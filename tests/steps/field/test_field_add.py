from frictionless import Resource, transform, steps


# General


def test_step_field_add():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.field_add(name="note", type="string", value="eu"),
        ],
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


def test_step_field_add_with_position():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.field_add(name="note", position=1, value="eu"),
        ],
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


def test_step_field_add_with_formula():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.table_normalize(),
            steps.field_add(name="calc", formula="id * 100 + population"),
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


def test_step_field_add_with_function():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.table_normalize(),
            steps.field_add(
                name="calc", function=lambda row: row["id"] * 100 + row["population"]
            ),
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


def test_step_field_add_with_incremental():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.field_add(name="number", incremental=True),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "number"},
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"number": 1, "id": 1, "name": "germany", "population": 83},
        {"number": 2, "id": 2, "name": "france", "population": 66},
        {"number": 3, "id": 3, "name": "spain", "population": 47},
    ]
