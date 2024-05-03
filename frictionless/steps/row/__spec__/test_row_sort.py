from frictionless import Pipeline, Step, steps
from frictionless.resources import TableResource

# General


def test_step_row_sort():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_sort(field_names=["name"]),
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
        {"id": 1, "name": "germany", "population": 83},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_row_sort_with_reverse():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_sort(field_names=["id"], reverse=True),
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
        {"id": 3, "name": "spain", "population": 47},
        {"id": 2, "name": "france", "population": 66},
        {"id": 1, "name": "germany", "population": 83},
    ]


# Bugs


def test_step_row_sort_with_reverse_in_desriptor_issue_996():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            Step.from_descriptor(
                {"type": "row-sort", "fieldNames": ["id"], "reverse": True}
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
        {"id": 3, "name": "spain", "population": 47},
        {"id": 2, "name": "france", "population": 66},
        {"id": 1, "name": "germany", "population": 83},
    ]
