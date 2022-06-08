from frictionless import Resource, Pipeline, steps


# General


def test_step_table_melt():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_melt(field_name="name"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "variable"},
            {"name": "value"},
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
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_melt(field_name="name", variables=["population"]),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "variable"},
            {"name": "value"},
        ]
    }
    assert target.read_rows() == [
        {"name": "germany", "variable": "population", "value": 83},
        {"name": "france", "variable": "population", "value": 66},
        {"name": "spain", "variable": "population", "value": 47},
    ]


def test_step_table_melt_with_to_field_names():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_melt(
                field_name="name", variables=["population"], to_field_names=["key", "val"]
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "key"},
            {"name": "val"},
        ]
    }
    assert target.read_rows() == [
        {"name": "germany", "key": "population", "val": 83},
        {"name": "france", "key": "population", "val": 66},
        {"name": "spain", "key": "population", "val": 47},
    ]
