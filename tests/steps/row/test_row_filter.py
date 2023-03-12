from frictionless import Pipeline, steps
from frictionless.resources import TableResource


# General


def test_step_row_filter():
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
    source = TableResource("data/transform.csv")
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
