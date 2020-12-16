import pytest
from frictionless import Resource, transform, steps


# Add


def test_step_field_add():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.field_add(name="note", type="string", value="eu"),
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
    assert target.read_rows(dict=True) == [
        {"id": 1, "name": "germany", "population": 83, "note": "eu"},
        {"id": 2, "name": "france", "population": 66, "note": "eu"},
        {"id": 3, "name": "spain", "population": 47, "note": "eu"},
    ]


def test_step_field_add_with_position():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.field_add(name="note", position=1, value="eu"),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "note"},
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows(dict=True) == [
        {"note": "eu", "id": 1, "name": "germany", "population": 83},
        {"note": "eu", "id": 2, "name": "france", "population": 66},
        {"note": "eu", "id": 3, "name": "spain", "population": 47},
    ]


@pytest.mark.skip
def test_step_field_add_with_formula():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.field_add(name="calc", value="<formula>id * 100 + population"),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "calc"},
        ]
    }
    assert target.read_rows(dict=True) == [
        {"id": 1, "name": "germany", "population": 83, "calc": 183},
        {"id": 2, "name": "france", "population": 66, "calc": 266},
        {"id": 3, "name": "spain", "population": 47, "calc": 347},
    ]


@pytest.mark.skip
def test_step_field_add_with_value_callable():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.field_add(
                name="calc", value=lambda row: row["id"] * 100 + row["population"]
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "calc"},
        ]
    }
    assert target.read_rows(dict=True) == [
        {"id": 1, "name": "germany", "population": 83, "calc": 183},
        {"id": 2, "name": "france", "population": 66, "calc": 266},
        {"id": 3, "name": "spain", "population": 47, "calc": 347},
    ]


def test_step_field_add_with_incremental():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.field_add(name="number", incremental=True),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "number"},
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows(dict=True) == [
        {"number": 1, "id": 1, "name": "germany", "population": 83},
        {"number": 2, "id": 2, "name": "france", "population": 66},
        {"number": 3, "id": 3, "name": "spain", "population": 47},
    ]


# Filter


def test_step_field_filter():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.field_filter(names=["id", "name"]),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }
    assert target.read_rows(dict=True) == [
        {"id": 1, "name": "germany"},
        {"id": 2, "name": "france"},
        {"id": 3, "name": "spain"},
    ]


# Move


def test_step_field_move():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.field_move(name="id", position=3),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "id", "type": "integer"},
        ]
    }
    assert target.read_rows(dict=True) == [
        {"name": "germany", "population": 83, "id": 1},
        {"name": "france", "population": 66, "id": 2},
        {"name": "spain", "population": 47, "id": 3},
    ]


# Remove


def test_step_field_remove():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.field_remove(names=["id"]),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows(dict=True) == [
        {"name": "germany", "population": 83},
        {"name": "france", "population": 66},
        {"name": "spain", "population": 47},
    ]


# Split


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
    assert target.read_rows(dict=True) == [
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
    assert target.read_rows(dict=True) == [
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
    assert target.read_rows(dict=True) == [
        {"id": 1, "population": 83, "name1": "ge", "name2": "rmany"},
        {"id": 2, "population": 66, "name1": "fr", "name2": "ance"},
        {"id": 3, "population": 47, "name1": "sp", "name2": "ain"},
    ]


# Unpack


def test_step_field_unpack():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.field_update(name="id", type="array", value=[1, 1]),
            steps.field_unpack(name="id", to_names=["id2", "id3"]),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "id2"},
            {"name": "id3"},
        ]
    }
    assert target.read_rows(dict=True) == [
        {"name": "germany", "population": 83, "id2": 1, "id3": 1},
        {"name": "france", "population": 66, "id2": 1, "id3": 1},
        {"name": "spain", "population": 47, "id2": 1, "id3": 1},
    ]


def test_step_field_unpack_with_preserve():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.field_update(name="id", type="array", value=[1, 1]),
            steps.field_unpack(name="id", to_names=["id2", "id3"], preserve=True),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "array"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "id2"},
            {"name": "id3"},
        ]
    }
    assert target.read_rows(dict=True) == [
        {"id": [1, 1], "name": "germany", "population": 83, "id2": 1, "id3": 1},
        {"id": [1, 1], "name": "france", "population": 66, "id2": 1, "id3": 1},
        {"id": [1, 1], "name": "spain", "population": 47, "id2": 1, "id3": 1},
    ]


def test_step_field_unpack_source_is_object():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.field_update(name="id", type="object", value={"note": "eu"}),
            steps.field_unpack(name="id", to_names=["note"]),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note"},
        ]
    }
    assert target.read_rows(dict=True) == [
        {"name": "germany", "population": 83, "note": "eu"},
        {"name": "france", "population": 66, "note": "eu"},
        {"name": "spain", "population": 47, "note": "eu"},
    ]


# Update


def test_step_field_update():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.field_update(name="id", type="string", value=str),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows(dict=True) == [
        {"id": "1", "name": "germany", "population": 83},
        {"id": "2", "name": "france", "population": 66},
        {"id": "3", "name": "spain", "population": 47},
    ]


def test_step_field_update_with_exact_value():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.field_update(name="id", type="string", value="x"),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows(dict=True) == [
        {"id": "x", "name": "germany", "population": 83},
        {"id": "x", "name": "france", "population": 66},
        {"id": "x", "name": "spain", "population": 47},
    ]
