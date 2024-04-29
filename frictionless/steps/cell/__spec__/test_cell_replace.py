from frictionless import Pipeline, steps
from frictionless.resources import TableResource

# General


def test_step_cell_replace():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.cell_replace(pattern="france", replace="FRANCE"),
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


def test_step_cell_replace_with_field_name():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.cell_replace(pattern="france", replace="FRANCE", field_name="id"),
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
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_cell_replace_using_regex():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.cell_replace(
                pattern="<regex>.*r.*", replace="center", field_name="name"
            ),
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
        {"id": 1, "name": "center", "population": 83},
        {"id": 2, "name": "center", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]
