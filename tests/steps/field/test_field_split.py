from frictionless import Resource, transform, steps


# General


def test_step_field_split():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.field_split(name="name", to_names=["name1", "name2"], pattern="a"),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "population", "type": "integer"},
            {"name": "name1", "type": "string"},
            {"name": "name2", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "population": 83, "name1": "germ", "name2": "ny"},
        {"id": 2, "population": 66, "name1": "fr", "name2": "nce"},
        {"id": 3, "population": 47, "name1": "sp", "name2": "in"},
    ]


def test_step_field_split_with_preserve():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.field_split(
                name="name", to_names=["name1", "name2"], pattern="a", preserve=True
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "name1", "type": "string"},
            {"name": "name2", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "name1": "germ", "name2": "ny"},
        {"id": 2, "name": "france", "population": 66, "name1": "fr", "name2": "nce"},
        {"id": 3, "name": "spain", "population": 47, "name1": "sp", "name2": "in"},
    ]


def test_step_field_split_with_capturing_groups():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.field_split(
                name="name", to_names=["name1", "name2"], pattern=r"(.{2})(.*)"
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "population", "type": "integer"},
            {"name": "name1", "type": "string"},
            {"name": "name2", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "population": 83, "name1": "ge", "name2": "rmany"},
        {"id": 2, "population": 66, "name1": "fr", "name2": "ance"},
        {"id": 3, "population": 47, "name1": "sp", "name2": "ain"},
    ]
