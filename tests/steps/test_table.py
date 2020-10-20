from frictionless import Resource, transform_resource, steps


# Merge Table


def test_step_merge_table():
    source = Resource(path="data/transform.csv")
    target = transform_resource(
        source,
        steps=[
            steps.merge_table(
                resource=Resource(data=[["id", "name", "note"], [4, "malta", "island"]])
            )
        ],
    )
    assert target.schema == {
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


def test_step_merge_table_with_names():
    source = Resource(path="data/transform.csv")
    target = transform_resource(
        source,
        steps=[
            steps.merge_table(
                resource=Resource(data=[["id", "name", "note"], [4, "malta", "island"]]),
                names=["id", "name"],
            )
        ],
    )
    assert target.schema == {
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
