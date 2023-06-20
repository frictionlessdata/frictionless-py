import pytest

from frictionless import Package, Pipeline, steps
from frictionless.resources import TableResource

# General


def test_resource_transform():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
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


def test_transform_resource_with_melt():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_melt(field_name="id"),
        ],
    )
    target = source.transform(pipeline)
    assert isinstance(target, TableResource)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "variable", "type": "string"},
            {"name": "value", "type": "any"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "variable": "name", "value": "germany"},
        {"id": 1, "variable": "population", "value": 83},
        {"id": 2, "variable": "name", "value": "france"},
        {"id": 2, "variable": "population", "value": 66},
        {"id": 3, "variable": "name", "value": "spain"},
        {"id": 3, "variable": "population", "value": 47},
    ]


def test_resource_transform_cell_set():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline.from_descriptor(
        {
            "steps": [
                {"type": "cell-set", "fieldName": "population", "value": 100},
            ],
        }
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
        {"id": 1, "name": "germany", "population": 100},
        {"id": 2, "name": "france", "population": 100},
        {"id": 3, "name": "spain", "population": 100},
    ]


@pytest.mark.skip
@pytest.mark.ci
def test_resource_transform_table_creation_with_foreign_key(sqlite_url):
    # write table
    resource = TableResource.from_descriptor(
        {
            "name": "commune",
            "schema": {
                "fields": [{"name": "insee_com", "type": "string"}],
                "primaryKey": ["insee_com"],
            },
            "data": [["insee_com"], ["01001"], ["01002"]],
        }
    )
    source = Package(resources=[resource])
    source.publish(sqlite_url)

    # write table using pipeline step
    package = Package("data/package-with-pipeline.json")
    package.resources[0].path = sqlite_url
    package.resources[1].pipeline.steps[0].path = sqlite_url  # type: ignore
    for resource in package.resources:
        if resource.pipeline:  # type: ignore
            resource.transform()  # type: ignore

    # read tables
    target = Package(sqlite_url)
    assert target.get_resource("zrr").schema.to_descriptor() == {
        "fields": [
            {"name": "CODGEO", "type": "string"},
            {"name": "LIBGEO", "type": "string"},
            {"name": "ZRR_SIMP", "type": "string"},
            {"name": "ZONAGE_ZRR", "type": "string"},
        ],
        "foreignKeys": [
            {
                "fields": ["CODGEO"],
                "reference": {"resource": "commune", "fields": ["insee_com"]},
            }
        ],
    }


@pytest.mark.skip
@pytest.mark.ci
def test_resource_transform_multiple_table_creation_with_foreign_key(sqlite_url):
    # write table
    resource = TableResource.from_descriptor(
        {
            "name": "commune",
            "schema": {
                "fields": [{"name": "insee_com", "type": "string"}],
                "primaryKey": ["insee_com"],
            },
            "data": [["insee_com"], ["01001"], ["01002"]],
        }
    )
    source = Package(resources=[resource])
    source.publish(sqlite_url)

    # write table using pipeline step
    package = Package("data/package-with-pipeline-multiple-tables-to-write.json")
    package.resources[0].path = sqlite_url
    package.resources[1].pipeline.steps[0].path = sqlite_url  # type: ignore
    package.resources[2].pipeline.steps[0].path = sqlite_url  # type: ignore

    for resource in package.resources:
        if resource.pipeline:  # type: ignore
            resource.transform()  # type: ignore

    # read tables
    target = Package(sqlite_url)
    assert target.get_resource("zrr").schema.to_descriptor() == {
        "fields": [
            {"name": "CODGEO", "type": "string"},
            {"name": "LIBGEO", "type": "string"},
            {"name": "ZRR_SIMP", "type": "string"},
            {"name": "ZONAGE_ZRR", "type": "string"},
        ],
        "foreignKeys": [
            {
                "fields": ["CODGEO"],
                "reference": {"resource": "commune", "fields": ["insee_com"]},
            }
        ],
    }
