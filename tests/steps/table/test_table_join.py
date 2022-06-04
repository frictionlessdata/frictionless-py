from frictionless import Resource, steps


# General


def test_step_table_join():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=Resource(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
                field_name="id",
            ),
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


def test_step_table_join_from_dict():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=dict(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
                field_name="id",
            ),
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


def test_step_table_join_with_name_is_not_first_field():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[
            steps.table_join(
                resource=Resource(
                    data=[["name", "note"], ["germany", "beer"], ["france", "vine"]]
                ),
                field_name="name",
            ),
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


def test_step_table_join_mode_left():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=Resource(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
                field_name="id",
                mode="left",
            ),
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


def test_step_table_join_mode_left_from_descriptor_issue_996():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[
            steps.table_normalize(),
            steps.table_join(
                {"fieldName": "id", "mode": "left"},
                resource=Resource(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
            ),
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


def test_step_table_join_mode_right():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=Resource(data=[["id", "note"], [1, "beer"], [4, "rum"]]),
                field_name="id",
                mode="right",
            ),
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


def test_step_table_join_mode_outer():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=Resource(data=[["id", "note"], [1, "beer"], [4, "rum"]]),
                field_name="id",
                mode="outer",
            ),
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


def test_step_table_join_mode_cross():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[
            steps.table_join(
                resource=Resource(data=[["id2", "note"], [1, "beer"], [4, "rum"]]),
                mode="cross",
            ),
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


def test_step_table_join_mode_negate():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[
            steps.table_join(
                resource=Resource(data=[["id", "note"], ["1", "beer"], ["4", "rum"]]),
                mode="negate",
            ),
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
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_table_join_hash_is_true():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=Resource(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
                field_name="id",
                use_hash=True,
            ),
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
