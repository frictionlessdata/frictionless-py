from frictionless import Resource, transform, steps


# Merge Tables


def test_step_merge_tables():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.merge_tables(
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


def test_step_merge_tables_with_names():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.merge_tables(
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


def test_step_merge_ignore_names():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.merge_tables(
                resource=Resource(data=[["id2", "name2"], [4, "malta"]]),
                ignore_names=True,
            )
        ],
    )
    assert target.schema == {
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


# Join Tables


def test_step_join_tables():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.join_tables(
                resource=Resource(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
                name="id",
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
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 2, "name": "france", "population": 66, "note": "vine"},
    ]


def test_step_join_tables_with_name_is_not_first_field():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.join_tables(
                resource=Resource(
                    data=[["name", "note"], ["germany", "beer"], ["france", "vine"]]
                ),
                name="name",
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
        {"id": 2, "name": "france", "population": 66, "note": "vine"},
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
    ]


def test_step_join_tables_mode_left():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.join_tables(
                resource=Resource(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
                name="id",
                mode="left",
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
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 2, "name": "france", "population": 66, "note": "vine"},
        {"id": 3, "name": "spain", "population": 47, "note": None},
    ]


def test_step_join_tables_mode_right():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.join_tables(
                resource=Resource(data=[["id", "note"], [1, "beer"], [4, "rum"]]),
                name="id",
                mode="right",
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
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 4, "name": None, "population": None, "note": "rum"},
    ]


def test_step_join_tables_mode_outer():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.join_tables(
                resource=Resource(data=[["id", "note"], [1, "beer"], [4, "rum"]]),
                name="id",
                mode="outer",
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
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 2, "name": "france", "population": 66, "note": None},
        {"id": 3, "name": "spain", "population": 47, "note": None},
        {"id": 4, "name": None, "population": None, "note": "rum"},
    ]


def test_step_join_tables_mode_cross():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.join_tables(
                resource=Resource(data=[["id2", "note"], [1, "beer"], [4, "rum"]]),
                mode="cross",
            )
        ],
    )
    assert target.schema == {
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
