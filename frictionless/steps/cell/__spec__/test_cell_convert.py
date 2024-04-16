from frictionless import Pipeline, steps
from frictionless.resources import TableResource

# General


def test_step_cell_convert():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", descriptor={"type": "string"}),
            steps.field_update(name="population", descriptor={"type": "string"}),
            steps.cell_convert(value="n/a"),
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
        {"id": "n/a", "name": "n/a", "population": "n/a"},
        {"id": "n/a", "name": "n/a", "population": "n/a"},
        {"id": "n/a", "name": "n/a", "population": "n/a"},
    ]


def test_step_cell_convert_with_field_name():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.cell_convert(field_name="name", value="n/a"),
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
        {"id": 1, "name": "n/a", "population": 83},
        {"id": 2, "name": "n/a", "population": 66},
        {"id": 3, "name": "n/a", "population": 47},
    ]
