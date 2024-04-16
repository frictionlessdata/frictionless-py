from frictionless import Pipeline, Step, steps
from frictionless.resources import TableResource

# General


def test_step_table_diff():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_diff(
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
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_table_diff_from_dict():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            Step.from_descriptor(
                {
                    "type": "table-diff",
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
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_table_diff_with_ignore_order():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_diff(
                resource=TableResource(
                    data=[
                        ["name", "id", "population"],
                        ["germany", "1", "83"],
                        ["france", "2", "50"],
                        ["spain", "3", "47"],
                    ]
                ),
                ignore_order=True,
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
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_table_diff_with_use_hash():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_diff(
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
        {"id": 2, "name": "france", "population": 66},
    ]
