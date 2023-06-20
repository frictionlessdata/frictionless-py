import pytest

from frictionless import Resource, platform

BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_dereference():
    resource = Resource(path="data/table.csv", schema="data/schema.json")
    resource.infer(stats=True)
    assert resource.to_descriptor() == {
        "name": "table",
        "type": "table",
        "path": "data/table.csv",
        "scheme": "file",
        "format": "csv",
        "mediatype": "text/csv",
        "encoding": "utf-8",
        "hash": "sha256:a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8",
        "bytes": 30,
        "fields": 2,
        "rows": 2,
        "schema": "data/schema.json",
    }


def test_resource_dereference_forced():
    resource = Resource("data/resource-with-dereferencing.json")
    resource.dereference()
    descriptor = resource.to_descriptor()
    assert isinstance(descriptor["dialect"], dict)
    assert isinstance(descriptor["schema"], dict)


def test_resource_dialect_schema_from_path():
    resource = Resource("data/resource-with-dereferencing.json")
    assert resource.to_descriptor() == {
        "name": "name",
        "type": "table",
        "path": "table.csv",
        "scheme": "file",
        "format": "csv",
        "mediatype": "text/csv",
        "dialect": "dialect.json",
        "schema": "schema.json",
    }
    assert resource.dialect.to_descriptor() == {
        "csv": {"delimiter": ";"},
    }
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }


@pytest.mark.vcr
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_dialect_schema_from_path_remote():
    resource = Resource(BASEURL % "data/resource-with-dereferencing.json")
    assert resource.to_descriptor() == {
        "name": "name",
        "type": "table",
        "path": "table.csv",
        "scheme": "file",
        "format": "csv",
        "mediatype": "text/csv",
        "dialect": "dialect.json",
        "schema": "schema.json",
    }
    assert resource.dialect.to_descriptor() == {
        "csv": {"delimiter": ";"},
    }
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }


def test_resource_schema_from_path_with_basepath():
    descriptor = {"name": "name", "path": "table.csv", "schema": "schema.json"}
    resource = Resource(descriptor, basepath="data")
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }
