import pytest
from frictionless import Resource, Pipeline, steps

pytestmark = pytest.mark.skip


# General


def test_step_row_filter():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula="id > 1"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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


def test_step_row_filter_with_function():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(function=lambda row: row["id"] > 1),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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


def test_step_row_filter_petl_selectop():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula="id == 1"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
    ]


def test_step_row_filter_petl_selecteq():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula="id == 1"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
    ]


def test_step_row_filter_petl_selectne():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula="id != 1"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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


def test_step_row_filter_petl_selectlt():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula="id < 2"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
    ]


def test_step_row_filter_petl_selectle():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula="id <= 2"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_row_filter_petl_selectgt():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula="id > 2"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_row_filter_petl_selectge():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula="id >= 2"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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


def test_step_row_filter_petl_selectrangeopen():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula="1 <= id <= 3"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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
    ]


def test_step_row_filter_petl_selectrangeopenleft():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula="1 <= id < 3"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_row_filter_petl_selectrangeopenright():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula="1 < id <= 3"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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


def test_step_row_filter_petl_selectrangeclosed():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula="1 < id < 3"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_row_filter_petl_selectcontains():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_filter(formula="'er' in name"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
    ]


def test_step_row_filter_petl_selectin():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula="id in [1]"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
    ]


def test_step_row_filter_petl_selectnoin():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula="id not in [2, 3]"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
    ]


def test_step_row_filter_petl_selectis():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula="id is 1"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
    ]


def test_step_row_filter_petl_selectisnot():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(formula="id is not 1"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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


def test_step_row_filter_petl_selectisinstance():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.row_filter(function=lambda row: isinstance(row["id"], int)),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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
    ]


def test_step_row_filter_petl_selectistrue():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_filter(function=lambda row: bool(row["id"])),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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
    ]


def test_step_row_filter_petl_selectisfalse():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_filter(function=lambda row: not bool(row["id"])),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == []


def test_step_row_filter_petl_selectnone():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_filter(formula="id is None"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == []


def test_step_row_filter_petl_selectisnone():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_filter(formula="id is not None"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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
    ]


def test_step_row_filter_petl_rowlenselect():
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_filter(function=lambda row: len(row) == 3),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
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
    ]
