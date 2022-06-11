from frictionless import Resource, Pipeline, steps


# General


def test_step_row_ungroup_first():
    source = Resource("data/transform-groups.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_ungroup(group_name="name", selection="first"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "year", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 3, "name": "france", "population": 66, "year": 2020},
        {"id": 1, "name": "germany", "population": 83, "year": 2020},
        {"id": 5, "name": "spain", "population": 47, "year": 2020},
    ]


def test_step_row_ungroup_last():
    source = Resource("data/transform-groups.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_ungroup(group_name="name", selection="last"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "year", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 4, "name": "france", "population": 54, "year": 1920},
        {"id": 2, "name": "germany", "population": 77, "year": 1920},
        {"id": 6, "name": "spain", "population": 33, "year": 1920},
    ]


def test_step_row_ungroup_min():
    source = Resource("data/transform-groups.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_ungroup(
                group_name="name", selection="min", value_name="population"
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "year", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 4, "name": "france", "population": 54, "year": 1920},
        {"id": 2, "name": "germany", "population": 77, "year": 1920},
        {"id": 6, "name": "spain", "population": 33, "year": 1920},
    ]


def test_step_row_ungroup_max():
    source = Resource("data/transform-groups.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_ungroup(
                group_name="name", selection="max", value_name="population"
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "year", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 3, "name": "france", "population": 66, "year": 2020},
        {"id": 1, "name": "germany", "population": 83, "year": 2020},
        {"id": 5, "name": "spain", "population": 47, "year": 2020},
    ]
