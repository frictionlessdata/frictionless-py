from frictionless import Pipeline, steps
from frictionless.resources import TableResource

# General


def test_step_field_unpack():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", value=[1, 1], descriptor={"type": "array"}),
            steps.field_unpack(name="id", to_names=["id2", "id3"]),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "id2", "type": "any"},
            {"name": "id3", "type": "any"},
        ]
    }
    assert target.read_rows() == [
        {"name": "germany", "population": 83, "id2": 1, "id3": 1},
        {"name": "france", "population": 66, "id2": 1, "id3": 1},
        {"name": "spain", "population": 47, "id2": 1, "id3": 1},
    ]


def test_step_field_unpack_with_preserve():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", value=[1, 1], descriptor={"type": "array"}),
            steps.field_unpack(name="id", to_names=["id2", "id3"], preserve=True),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "array"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "id2", "type": "any"},
            {"name": "id3", "type": "any"},
        ]
    }
    assert target.read_rows() == [
        {"id": [1, 1], "name": "germany", "population": 83, "id2": 1, "id3": 1},
        {"id": [1, 1], "name": "france", "population": 66, "id2": 1, "id3": 1},
        {"id": [1, 1], "name": "spain", "population": 47, "id2": 1, "id3": 1},
    ]


def test_step_field_unpack_source_is_object():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(
                name="id",
                value={"note": "eu"},
                descriptor={"type": "object"},
            ),
            steps.field_unpack(name="id", to_names=["note"]),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "any"},
        ]
    }
    assert target.read_rows() == [
        {"name": "germany", "population": 83, "note": "eu"},
        {"name": "france", "population": 66, "note": "eu"},
        {"name": "spain", "population": 47, "note": "eu"},
    ]
