from frictionless import Resource, transform, steps


# General


def test_step_row_search():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[
            steps.row_search(regex=r"^f.*"),
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
    ]


def test_step_row_search_with_name():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[
            steps.row_search(regex=r"^f.*", field_name="name"),
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
    ]


def test_step_row_search_with_negate():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[
            steps.row_search(regex=r"^f.*", negate=True),
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
        {"id": 3, "name": "spain", "population": 47},
    ]
