from frictionless import Pipeline, steps
from frictionless.resources import TableResource

# General


def test_step_field_update():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", function=str, descriptor={"type": "string"}),
            steps.field_update(name="population", formula="int(population)*2"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": "1", "name": "germany", "population": 83 * 2},
        {"id": "2", "name": "france", "population": 66 * 2},
        {"id": "3", "name": "spain", "population": 47 * 2},
    ]


def test_step_field_update_with_exact_value():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", value="x", descriptor={"type": "string"}),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", descriptor={"name": "new-name"}),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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
