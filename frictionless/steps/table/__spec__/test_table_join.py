from frictionless import Pipeline, Step, steps
from frictionless.resources import TableResource

# General


def test_step_table_join():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=TableResource(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
                field_name="id",
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 2, "name": "france", "population": 66, "note": "vine"},
    ]


def test_step_table_join_from_dict():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            Step.from_descriptor(
                {
                    "type": "table-join",
                    "fieldName": "id",
                    "resource": {
                        "name": "data",
                        "data": [["id", "note"], [1, "beer"], [2, "vine"]],
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
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 2, "name": "france", "population": 66, "note": "vine"},
    ]


def test_step_table_join_with_name_is_not_first_field():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_join(
                resource=TableResource(
                    data=[["name", "note"], ["germany", "beer"], ["france", "vine"]]
                ),
                field_name="name",
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66, "note": "vine"},
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
    ]


def test_step_table_join_mode_left():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=TableResource(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
                field_name="id",
                mode="left",
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 2, "name": "france", "population": 66, "note": "vine"},
        {"id": 3, "name": "spain", "population": 47, "note": None},
    ]


def test_step_table_join_mode_right():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=TableResource(data=[["id", "note"], [1, "beer"], [4, "rum"]]),
                field_name="id",
                mode="right",
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 4, "name": None, "population": None, "note": "rum"},
    ]


def test_step_table_join_mode_outer():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=TableResource(data=[["id", "note"], [1, "beer"], [4, "rum"]]),
                field_name="id",
                mode="outer",
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 2, "name": "france", "population": 66, "note": None},
        {"id": 3, "name": "spain", "population": 47, "note": None},
        {"id": 4, "name": None, "population": None, "note": "rum"},
    ]


def test_step_table_join_mode_cross():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_join(
                resource=TableResource(data=[["id2", "note"], [1, "beer"], [4, "rum"]]),
                mode="cross",
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "id2", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "id2": 1, "note": "beer"},
        {"id": 1, "name": "germany", "population": 83, "id2": 4, "note": "rum"},
        {"id": 2, "name": "france", "population": 66, "id2": 1, "note": "beer"},
        {"id": 2, "name": "france", "population": 66, "id2": 4, "note": "rum"},
        {"id": 3, "name": "spain", "population": 47, "id2": 1, "note": "beer"},
        {"id": 3, "name": "spain", "population": 47, "id2": 4, "note": "rum"},
    ]


def test_step_table_join_mode_negate():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_join(
                resource=TableResource(
                    data=[["id", "note"], ["1", "beer"], ["4", "rum"]]
                ),
                mode="negate",
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
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_table_join_hash_is_true():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=TableResource(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
                field_name="id",
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
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 2, "name": "france", "population": 66, "note": "vine"},
    ]


# Bugs


def test_step_table_join_mode_left_from_descriptor_issue_996():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            Step.from_descriptor(
                {
                    "type": "table-join",
                    "fieldName": "id",
                    "mode": "left",
                    "resource": {
                        "name": "data",
                        "data": [["id", "note"], [1, "beer"], [2, "vine"]],
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
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 2, "name": "france", "population": 66, "note": "vine"},
        {"id": 3, "name": "spain", "population": 47, "note": None},
    ]
