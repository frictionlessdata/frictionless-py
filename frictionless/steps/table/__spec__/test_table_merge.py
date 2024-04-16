from frictionless import Pipeline, Step, steps
from frictionless.resources import TableResource

# General


def test_step_table_merge():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_merge(
                resource=TableResource(
                    data=[["id", "name", "note"], [4, "malta", "island"]]
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
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": None},
        {"id": 2, "name": "france", "population": 66, "note": None},
        {"id": 3, "name": "spain", "population": 47, "note": None},
        {"id": 4, "name": "malta", "population": None, "note": "island"},
    ]


def test_step_table_merge_from_dict():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            Step.from_descriptor(
                {
                    "type": "table-merge",
                    "resource": dict(
                        name="target-resource",
                        data=[["id", "name", "note"], [4, "malta", "island"]],
                    ),
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
        {"id": 1, "name": "germany", "population": 83, "note": None},
        {"id": 2, "name": "france", "population": 66, "note": None},
        {"id": 3, "name": "spain", "population": 47, "note": None},
        {"id": 4, "name": "malta", "population": None, "note": "island"},
    ]


def test_step_table_merge_with_field_names():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_merge(
                resource=TableResource(
                    data=[["id", "name", "note"], [4, "malta", "island"]]
                ),
                field_names=["id", "name"],
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany"},
        {"id": 2, "name": "france"},
        {"id": 3, "name": "spain"},
        {"id": 4, "name": "malta"},
    ]


def test_step_merge_ignore_fields():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_merge(
                resource=TableResource(data=[["id2", "name2"], [4, "malta"]]),
                ignore_fields=True,
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
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
        {"id": 4, "name": "malta", "population": None},
    ]


def test_step_table_merge_with_sort():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_merge(
                resource=TableResource(
                    name="target-resource",
                    data=[["id", "name", "population"], [4, "malta", 1]],
                ),
                sort_by_field=["population"],  # type: ignore
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
        {"id": 4, "name": "malta", "population": 1},
        {"id": 3, "name": "spain", "population": 47},
        {"id": 2, "name": "france", "population": 66},
        {"id": 1, "name": "germany", "population": 83},
    ]
