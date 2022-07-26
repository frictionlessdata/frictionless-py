import pytest
from frictionless import Resource, Pipeline, steps


# General


@pytest.mark.xfail(reason="steps")
def test_step_field_merge_907():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_merge(name="details", from_names=["name", "population"]),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "details", "type": "string"},
        ]
    }
    assert target.read_rows()[0] == {
        "id": 1,
        "details": "germany-83",
    }


@pytest.mark.xfail(reason="steps")
def test_step_field_merge_preserve_907():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_merge(
                name="details", from_names=["name", "population"], preserve=True
            )
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "details", "type": "string"},
        ]
    }
    assert target.read_rows()[0] == {
        "id": 1,
        "name": "germany",
        "population": 83,
        "details": "germany-83",
    }
