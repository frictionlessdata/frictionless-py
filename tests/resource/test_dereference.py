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
        "path": "data/table.csv",
        "type": "table",
        "scheme": "file",
        "format": "csv",
        "encoding": "utf-8",
        "mediatype": "text/csv",
        "dialect": {
            "controls": [
                {"code": "local"},
                {"code": "csv"},
            ]
        },
        "schema": "data/schema.json",
        "stats": {
            "hash": "6c2c61dd9b0e9c6876139a449ed87933",
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
