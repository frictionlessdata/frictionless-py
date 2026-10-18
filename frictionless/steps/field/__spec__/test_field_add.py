import pytest

from frictionless import Pipeline, Schema, steps
from frictionless.resources import TableResource

# General


def test_step_field_add():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_add(name="note", value="eu", descriptor={"type": "string"}),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "eu"},
        {"id": 2, "name": "france", "population": 66, "note": "eu"},
        {"id": 3, "name": "spain", "population": 47, "note": "eu"},
    ]


def test_step_field_add_with_position():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_add(name="note", position=1, value="eu"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "note", "type": "any"},
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"note": "eu", "id": 1, "name": "germany", "population": 83},
        {"note": "eu", "id": 2, "name": "france", "population": 66},
        {"note": "eu", "id": 3, "name": "spain", "population": 47},
    ]


def test_step_field_add_with_formula():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.field_add(name="calc", formula="id * 100 + population"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "calc", "type": "any"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "calc": 183},
        {"id": 2, "name": "france", "population": 66, "calc": 266},
        {"id": 3, "name": "spain", "population": 47, "calc": 347},
    ]


def test_step_field_add_with_function():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.field_add(
                name="calc", function=lambda row: row["id"] * 100 + row["population"]
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "calc", "type": "any"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "calc": 183},
        {"id": 2, "name": "france", "population": 66, "calc": 266},
        {"id": 3, "name": "spain", "population": 47, "calc": 347},
    ]


def test_step_field_add_with_incremental():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_add(name="number", incremental=True),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "number", "type": "integer"},
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"number": 1, "id": 1, "name": "germany", "population": 83},
        {"number": 2, "id": 2, "name": "france", "population": 66},
        {"number": 3, "id": 3, "name": "spain", "population": 47},
    ]


@pytest.mark.parametrize("value", [False, 0, 0.0, "", [], {}, ()])
def test_step_field_add_with_falsy_value(value):
    source = TableResource(
        data=[["id"], [1], [2]],
        schema=Schema.from_descriptor(
            {"fields": [{"name": "id", "type": "integer"}], "missingValues": []}
        ),
    )
    target = source.transform(Pipeline(steps=[steps.field_add(name="note", value=value)]))
    rows = target.read_rows()
    assert [row["note"] for row in rows] == [value, value]
    assert all(type(row["note"]) is type(value) for row in rows)


@pytest.mark.parametrize("value", [False, 0, "", [], {}, "constant"])
@pytest.mark.parametrize(
    "options",
    [
        {"function": lambda row: row["id"] * 10},
        {"formula": "id * 100"},
        {"formula": "id * 100", "function": lambda row: row["id"] * 10},
    ],
)
def test_step_field_add_value_takes_precedence(value, options):
    source = TableResource(
        data=[["id"], [1], [2]],
        schema=Schema.from_descriptor(
            {"fields": [{"name": "id", "type": "integer"}], "missingValues": []}
        ),
    )
    target = source.transform(
        Pipeline(steps=[steps.field_add(name="note", value=value, **options)])
    )
    assert [row["note"] for row in target.read_rows()] == [value, value]


@pytest.mark.parametrize(
    "options, expected",
    [
        ({}, [None, None]),
        ({"value": None}, [None, None]),
        ({"value": None, "function": lambda row: row["id"] * 10}, [10, 20]),
        ({"value": None, "formula": "id * 100"}, [100, 200]),
        (
            {
                "value": None,
                "formula": "id * 100",
                "function": lambda row: row["id"] * 10,
            },
            [100, 200],
        ),
    ],
)
def test_step_field_add_with_none_value(options, expected):
    source = TableResource(data=[["id"], [1], [2]])
    target = source.transform(Pipeline(steps=[steps.field_add(name="note", **options)]))
    assert [row["note"] for row in target.read_rows()] == expected


def test_step_field_add_with_false_value_csv_roundtrip(tmp_path):
    source_path = tmp_path / "source.csv"
    source_path.write_text("id\n1\n2\n", encoding="utf-8")
    source = TableResource(path=source_path.name, basepath=str(tmp_path))
    target = source.transform(
        Pipeline(
            steps=[
                steps.field_add(
                    name="flag",
                    value=False,
                    descriptor={
                        "type": "boolean",
                        "trueValues": ["Yes"],
                        "falseValues": ["No"],
                        "constraints": {"required": True},
                    },
                ),
            ]
        )
    )
    assert target.validate().valid
    target_path = tmp_path / "target.csv"
    target.write(str(target_path))
    restored = TableResource(
        path=target_path.name, basepath=str(tmp_path), schema=target.schema
    )
    assert restored.validate().valid
    assert restored.read_rows() == [{"id": 1, "flag": False}, {"id": 2, "flag": False}]
    assert target_path.read_text(encoding="utf-8") == "id,flag\n1,No\n2,No\n"
