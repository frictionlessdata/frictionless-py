from frictionless import Resource, transform, steps


# General


def test_step_cell_fill():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.cell_replace(pattern="france", replace=None),
            steps.cell_fill(field_name="name", value="FRANCE"),
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
        {"id": 2, "name": "FRANCE", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_cell_fill_direction_down():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.cell_replace(pattern="france", replace=None),
            steps.cell_fill(direction="down"),
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
        {"id": 2, "name": "germany", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_cell_fill_direction_right():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.field_update(name="id", type="string"),
            steps.field_update(name="population", type="string"),
            steps.cell_replace(pattern="france", replace=None),
            steps.cell_fill(direction="right"),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": "1", "name": "germany", "population": "83"},
        {"id": "2", "name": "2", "population": "66"},
        {"id": "3", "name": "spain", "population": "47"},
    ]


def test_step_cell_fill_direction_left():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.field_update(name="id", type="string"),
            steps.field_update(name="population", type="string"),
            steps.cell_replace(pattern="france", replace=None),
            steps.cell_fill(direction="left"),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": "1", "name": "germany", "population": "83"},
        {"id": "2", "name": "66", "population": "66"},
        {"id": "3", "name": "spain", "population": "47"},
    ]
