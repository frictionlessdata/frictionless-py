from frictionless import Resource, Pipeline, steps


# General


def test_step_field_filter():
    source = Resource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_filter(names=["id", "name"]),
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
    ]


# Bugs


def test_step_field_filter_should_not_change_the_order_issue_1155():
    source = Resource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_filter(names=["name", "id"]),
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
    ]
