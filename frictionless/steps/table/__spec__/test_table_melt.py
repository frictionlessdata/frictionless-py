from frictionless import Pipeline, steps
from frictionless.resources import TableResource

# General


def test_step_table_melt():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_melt(field_name="name"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "variable", "type": "string"},
            {"name": "value", "type": "any"},
        ]
    }
    assert target.read_rows() == [
        {"name": "germany", "variable": "id", "value": 1},
        {"name": "germany", "variable": "population", "value": 83},
        {"name": "france", "variable": "id", "value": 2},
        {"name": "france", "variable": "population", "value": 66},
        {"name": "spain", "variable": "id", "value": 3},
        {"name": "spain", "variable": "population", "value": 47},
    ]


def test_step_table_melt_with_variables():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_melt(field_name="name", variables=["population"]),  # type: ignore
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "variable", "type": "string"},
            {"name": "value", "type": "any"},
        ]
    }
    assert target.read_rows() == [
        {"name": "germany", "variable": "population", "value": 83},
        {"name": "france", "variable": "population", "value": 66},
        {"name": "spain", "variable": "population", "value": 47},
    ]


def test_step_table_melt_with_to_field_names():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_melt(
                field_name="name", variables=["population"], to_field_names=["key", "val"]  # type: ignore
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "key", "type": "string"},
            {"name": "val", "type": "any"},
        ]
    }
    assert target.read_rows() == [
        {"name": "germany", "key": "population", "val": 83},
        {"name": "france", "key": "population", "val": 66},
        {"name": "spain", "key": "population", "val": 47},
    ]
