from frictionless import Pipeline, steps
from frictionless.resources import TableResource

# General


def test_step_cell_fill():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.cell_replace(pattern="france", replace=None),  # type: ignore
            steps.cell_fill(field_name="name", value="FRANCE"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.cell_replace(pattern="france", replace=None),  # type: ignore
            steps.cell_fill(direction="down"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", descriptor={"type": "string"}),
            steps.field_update(name="population", descriptor={"type": "string"}),
            steps.cell_replace(pattern="france", replace=None),  # type: ignore
            steps.cell_fill(direction="right"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", descriptor={"type": "string"}),
            steps.field_update(name="population", descriptor={"type": "string"}),
            steps.cell_replace(pattern="france", replace=None),  # type: ignore
            steps.cell_fill(direction="left"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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
