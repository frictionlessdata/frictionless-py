from frictionless import Resource, transform, steps


# General


def test_step_table_diff():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_diff(
                resource=Resource(
                    data=[
                        ["id", "name", "population"],
                        [1, "germany", 83],
                        [2, "france", 50],
                        [3, "spain", 47],
                    ]
                )
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
    ]


def test_step_table_diff_from_dict():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_diff(
                resource=dict(
                    data=[
                        ["id", "name", "population"],
                        [1, "germany", 83],
                        [2, "france", 50],
                        [3, "spain", 47],
                    ]
                )
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
    ]


def test_step_table_diff_with_ignore_order():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_diff(
                resource=Resource(
                    data=[
                        ["name", "id", "population"],
                        ["germany", "1", "83"],
                        ["france", "2", "50"],
                        ["spain", "3", "47"],
                    ]
                ),
                ignore_order=True,
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
    ]


def test_step_table_diff_with_use_hash():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_diff(
                resource=Resource(
                    data=[
                        ["id", "name", "population"],
                        [1, "germany", 83],
                        [2, "france", 50],
                        [3, "spain", 47],
                    ]
                ),
                use_hash=True,
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
    ]
