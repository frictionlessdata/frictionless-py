from frictionless import Pipeline, Step, steps
from frictionless.resources import TableResource

# General


def test_step_table_intersect():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_intersect(
                resource=TableResource(
                    data=[
                        ["id", "name", "population"],
                        [1, "germany", 83],
                        [2, "france", 50],
                        [3, "spain", 47],
                    ]
                )
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
        {"id": 1, "name": "germany", "population": 83},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_table_intersect_from_dict():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            Step.from_descriptor(
                {
                    "type": "table-intersect",
                    "resource": {
                        "name": "data",
                        "data": [
                            ["id", "name", "population"],
                            [1, "germany", 83],
                            [2, "france", 50],
                            [3, "spain", 47],
                        ],
                    },
                }
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
        {"id": 1, "name": "germany", "population": 83},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_table_intersect_with_use_hash():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_intersect(
                resource=TableResource(
                    data=[
                        ["id", "name", "population"],
                        [1, "germany", 83],
                        [2, "france", 50],
                        [3, "spain", 47],
                    ]
                ),
                use_hash=True,
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
        {"id": 1, "name": "germany", "population": 83},
        {"id": 3, "name": "spain", "population": 47},
    ]
