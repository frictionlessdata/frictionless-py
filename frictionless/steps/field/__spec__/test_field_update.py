import pytest

from frictionless import Pipeline, steps, transform
from frictionless.package.package import Package
from frictionless.resources import TableResource
from frictionless.schema.schema import Schema

# General


def test_step_field_update():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", function=str, descriptor={"type": "string"}),
            steps.field_update(name="population", formula="int(population)*2"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": "1", "name": "germany", "population": 83 * 2},
        {"id": "2", "name": "france", "population": 66 * 2},
        {"id": "3", "name": "spain", "population": 47 * 2},
    ]


def test_step_field_update_with_exact_value():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", value="x", descriptor={"type": "string"}),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": "x", "name": "germany", "population": 83},
        {"id": "x", "name": "france", "population": 66},
        {"id": "x", "name": "spain", "population": 47},
    ]


@pytest.mark.parametrize("value", [False, 0, 0.0, "", [], {}, (), "constant"])
@pytest.mark.parametrize("rename", [False, True])
def test_step_field_update_with_falsy_value(value, rename):
    source = TableResource(
        data=[["note"], ["old"], ["previous"]],
        schema=Schema.from_descriptor(
            {"fields": [{"name": "note", "type": "any"}], "missingValues": []}
        ),
    )
    name = "updated_note" if rename else "note"
    descriptor = {"name": name} if rename else {}
    pipeline = Pipeline(
        steps=[steps.field_update(name="note", value=value, descriptor=descriptor)]
    )
    target = source.transform(pipeline)
    assert target.validate().valid
    rows = target.read_rows()
    assert [row[name] for row in rows] == [value, value]
    assert all(type(row[name]) is type(value) for row in rows)


@pytest.mark.parametrize("value", [False, 0, 0.0, "", [], "constant"])
@pytest.mark.parametrize("rename", [False, True])
def test_step_field_update_with_falsy_value_from_descriptor(value, rename):
    source = TableResource(
        data=[["note"], ["old"], ["previous"]],
        schema=Schema.from_descriptor(
            {"fields": [{"name": "note", "type": "any"}], "missingValues": []}
        ),
    )
    name = "updated_note" if rename else "note"
    descriptor = {"name": name} if rename else {}
    pipeline = Pipeline.from_descriptor(
        {
            "steps": [
                {
                    "type": "field-update",
                    "name": "note",
                    "value": value,
                    "descriptor": descriptor,
                }
            ]
        }
    )
    target = source.transform(pipeline)
    assert target.validate().valid
    rows = target.read_rows()
    assert [row[name] for row in rows] == [value, value]
    assert all(type(row[name]) is type(value) for row in rows)


@pytest.mark.parametrize("value", [False, 0, "", [], {}, "constant", None])
@pytest.mark.parametrize(
    "options, expected",
    [
        ({"function": lambda value: value * 10}, [10, 20]),
        ({"formula": "id * 100"}, [100, 200]),
        (
            {"formula": "id * 100", "function": lambda value: value * 10},
            [100, 200],
        ),
    ],
)
def test_step_field_update_function_and_formula_take_precedence(value, options, expected):
    source = TableResource(data=[["id"], [1], [2]])
    target = source.transform(
        Pipeline(steps=[steps.field_update(name="id", value=value, **options)])
    )
    assert [row["id"] for row in target.read_rows()] == expected


@pytest.mark.parametrize("options", [{}, {"value": None}])
@pytest.mark.parametrize("from_descriptor", [False, True])
def test_step_field_update_with_none_value(options, from_descriptor):
    source = TableResource(data=[["id"], [1], [2]])
    descriptor = {"title": "Identifier"}
    if from_descriptor:
        pipeline = Pipeline.from_descriptor(
            {
                "steps": [
                    {
                        "type": "field-update",
                        "name": "id",
                        "descriptor": descriptor,
                        **options,
                    }
                ]
            }
        )
    else:
        pipeline = Pipeline(
            steps=[steps.field_update(name="id", descriptor=descriptor, **options)]
        )
    target = source.transform(pipeline)
    assert target.schema.get_field("id").title == "Identifier"
    assert target.read_rows() == [{"id": 1}, {"id": 2}]


@pytest.mark.parametrize("rename", [False, True])
def test_step_field_update_with_falsy_values_csv_roundtrip(tmp_path, rename):
    source_path = tmp_path / "source.csv"
    source_path.write_text("id,flag,count\n1,Yes,7\n2,Yes,9\n", encoding="utf-8")
    source = TableResource(
        path=source_path.name,
        basepath=str(tmp_path),
        schema=Schema.from_descriptor(
            {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {
                        "name": "flag",
                        "type": "boolean",
                        "trueValues": ["Yes"],
                        "falseValues": ["No"],
                        "constraints": {"required": True},
                    },
                    {
                        "name": "count",
                        "type": "integer",
                        "constraints": {"required": True},
                    },
                ]
            }
        ),
    )
    flag_name = "updated_flag" if rename else "flag"
    count_name = "updated_count" if rename else "count"
    pipeline = Pipeline.from_descriptor(
        {
            "steps": [
                {
                    "type": "field-update",
                    "name": "flag",
                    "value": False,
                    "descriptor": {"name": flag_name},
                },
                {
                    "type": "field-update",
                    "name": "count",
                    "value": 0,
                    "descriptor": {"name": count_name},
                },
            ]
        }
    )
    target = source.transform(pipeline)
    expected = [
        {"id": 1, flag_name: False, count_name: 0},
        {"id": 2, flag_name: False, count_name: 0},
    ]
    assert target.validate().valid
    assert target.read_rows() == expected
    target_path = tmp_path / "target.csv"
    target.write(str(target_path))
    assert (
        target_path.read_text(encoding="utf-8")
        == f"id,{flag_name},{count_name}\n1,No,0\n2,No,0\n"
    )
    restored = TableResource(
        path=target_path.name, basepath=str(tmp_path), schema=target.schema
    )
    assert restored.validate().valid
    rows = restored.read_rows()
    assert rows == expected
    assert all(row[flag_name] is False and type(row[count_name]) is int for row in rows)


@pytest.mark.parametrize("options", [{}, {"value": None}])
def test_step_field_update_new_name(options):
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", descriptor={"name": "new-name"}, **options),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "new-name", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"new-name": 1, "name": "germany", "population": 83},
        {"new-name": 2, "name": "france", "population": 66},
        {"new-name": 3, "name": "spain", "population": 47},
    ]


def test_step_field_update_field_name_with_primary_key():
    source = TableResource(path="data/transform.csv")
    source.schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
                {"name": "population", "type": "integer"},
            ],
            "primaryKey": ["id"],
        }
    )

    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", descriptor={"name": "pkey"}),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.primary_key == ["pkey"]


def test_step_field_update_referenced_as_foreign_key():
    resource1 = TableResource(name="resource1", path="data/transform.csv")
    resource2 = TableResource(name="resource2")
    resource1.schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
                {"name": "population", "type": "integer"},
            ],
            "primaryKey": ["id"],
        }
    )
    resource2.schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "address", "type": "string"},
                {"name": "country_name", "type": "integer"},
            ],
            "primaryKey": ["id"],
            "foreignKeys": [
                {
                    "fields": ["country_name"],
                    "reference": {"fields": ["id"], "resource": "resource1"},
                }
            ],
        }
    )
    package = Package(name="test-package", resources=[resource1, resource2])
    transform(
        package,
        steps=[
            steps.resource_transform(
                name="resource1",
                steps=[steps.field_update(name="id", descriptor={"name": "pkey"})],
            )
        ],
    )
    assert (
        package.get_resource("resource1").validate().flatten(["title", "message"]) == []
    )
    assert package.get_resource("resource1").schema.primary_key == ["pkey"]
    assert package.get_resource("resource2").schema.foreign_keys == [
        {
            "fields": ["country_name"],
            "reference": {"fields": ["pkey"], "resource": "resource1"},
        }
    ]


def test_step_field_update_with_function_and_pass_row_true():
    source = TableResource(path="data/transform.csv")

    def add_country_to_id(value, row):
        return str(value) + " " + row["name"]

    pipeline = Pipeline(
        steps=[
            steps.field_update(
                name="id",
                function=add_country_to_id,
                descriptor={"type": "string"},
                pass_row=True,
            )
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": "1 germany", "name": "germany", "population": 83},
        {"id": "2 france", "name": "france", "population": 66},
        {"id": "3 spain", "name": "spain", "population": 47},
    ]
