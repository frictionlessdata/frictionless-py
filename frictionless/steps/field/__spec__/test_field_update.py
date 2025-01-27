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


def test_step_field_update_new_name():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", descriptor={"name": "new-name"}),
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
                name="id", function=add_country_to_id,
                descriptor={"type": "string"}, pass_row=True)
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
