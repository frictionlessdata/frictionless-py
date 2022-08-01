import pytest
from frictionless import Resource


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


@pytest.mark.xfail(reason="dereference")
def test_resource_dereference():
    resource = Resource(path="data/table.csv", schema="data/schema.json")
    resource.infer(stats=True)
    assert resource.to_descriptor() == {
        "name": "table",
        "type": "table",
        "path": "data/table.csv",
        "scheme": "file",
        "format": "csv",
        "encoding": "utf-8",
        "mediatype": "text/csv",
        "schema": "data/schema.json",
        "stats": {
            "md5": "6c2c61dd9b0e9c6876139a449ed87933",
            "sha256": "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8",
            "bytes": 30,
            "fields": 2,
            "rows": 2,
        },
    }


@pytest.mark.xfail(reason="dereference")
def test_resource_schema_from_path():
    resource = Resource("data/resource-with-dereferencing.json")
    assert resource.to_descriptor() == {
        "name": "name",
        "path": "table.csv",
        "dialect": "dialect.json",
        "schema": "schema.json",
    }
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }


@pytest.mark.vcr
@pytest.mark.xfail(reason="dereference")
def test_resource_schema_from_path_remote():
    resource = Resource(BASEURL % "data/resource-with-dereferencing.json")
    assert resource.to_descriptor() == {
        "name": "name",
        "path": "table.csv",
        "dialect": "dialect.json",
        "schema": "schema.json",
    }
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }


@pytest.mark.xfail(reason="dereference")
def test_resource_dialect_from_path():
    resource = Resource("data/resource-with-dereferencing.json")
    assert resource.to_descriptor() == {
        "name": "name",
        "path": "table.csv",
        "dialect": "dialect.json",
        "schema": "schema.json",
    }
    assert resource.dialect.to_descriptor() == {
        "delimiter": ";",
    }


@pytest.mark.vcr
@pytest.mark.xfail(reason="dereference")
def test_resource_dialect_from_path_remote():
    resource = Resource(BASEURL % "data/resource-with-dereferencing.json")
    assert resource.to_descriptor() == {
        "name": "name",
        "path": "table.csv",
        "dialect": "dialect.json",
        "schema": "schema.json",
    }
    assert resource.dialect.to_descriptor() == {
        "delimiter": ";",
    }


@pytest.mark.xfail(reason="dereference")
def test_resource_schema_from_path_with_basepath():
    descriptor = {"name": "name", "path": "table.csv", "schema": "schema.json"}
    resource = Resource(descriptor, basepath="data")
    assert resource.to_descriptor() == descriptor
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }
