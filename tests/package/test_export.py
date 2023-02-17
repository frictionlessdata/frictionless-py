import os
import json
import yaml
import pytest
from frictionless import Package, Resource, describe_package, helpers
from frictionless.plugins.sql import SqlDialect


IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Export/Import


def test_package_to_copy():
    source = describe_package("data/chunk*.csv")
    target = source.to_copy()
    assert source is not target
    assert source == target


def test_package_to_json(tmpdir):
    # Write
    target = os.path.join(tmpdir, "package.json")
    package = Package("data/package.json")
    package.to_json(target)

    # Read
    with open(target, encoding="utf-8") as file:
        assert package == json.load(file)


def test_package_to_yaml(tmpdir):
    # Write
    target = os.path.join(tmpdir, "package.yaml")
    package = Package("data/package.json")
    package.to_yaml(target)

    # Read
    with open(target, encoding="utf-8") as file:
        assert package == yaml.safe_load(file)


def test_package_to_zip(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    source = Package("data/package.json")
    source.to_zip(path)
    target = Package.from_zip(path)
    assert target.name == "name"
    assert target.get_resource("name").name == "name"
    assert target.get_resource("name").path == "table.csv"
    assert target.get_resource("name").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_package_to_zip_resource_path(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    source = Package(resources=[Resource(path="data/table.csv")])
    source.to_zip(path)
    target = Package.from_zip(path)
    assert target.get_resource("table").path == "data/table.csv"
    assert target.get_resource("table").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_package_to_zip_resource_remote_path(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    source = Package(resources=[Resource(path=BASEURL % "data/table.csv")])
    source.to_zip(path)
    target = Package.from_zip(path)
    assert target.get_resource("table").path == BASEURL % "data/table.csv"
    assert target.get_resource("table").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_package_to_zip_resource_memory_inline(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    data = [["id", "name"], [1, "english"], [2, "中国人"]]
    source = Package(resources=[Resource(name="table", data=data)])
    source.to_zip(path)
    target = Package.from_zip(path)
    assert target.get_resource("table").data == data
    assert target.get_resource("table").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_package_to_zip_resource_memory_function(tmpdir):
    path = os.path.join(tmpdir, "package.zip")
    data = lambda: [["id", "name"], [1, "english"], [2, "中国人"]]
    source = Package(resources=[Resource(name="table", data=data)])
    if IS_UNIX:
        source.to_zip(path)
        target = Package.from_zip(path)
        assert target.get_resource("table").path == "table.csv"
        assert target.get_resource("table").read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_package_to_zip_resource_sql(tmpdir, database_url):
    path = os.path.join(tmpdir, "package.zip")
    dialect = SqlDialect(table="table")
    source = Package(resources=[Resource(database_url, name="table", dialect=dialect)])
    source.to_zip(path)
    target = Package.from_zip(path)
    assert target.get_resource("table").path == database_url
    assert target.get_resource("table").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_package_to_zip_resource_multipart(tmpdir, database_url):
    path = os.path.join(tmpdir, "package.zip")
    source = Package(resources=[Resource(path=["data/chunk1.csv", "data/chunk2.csv"])])
    source.to_zip(path)
    target = Package.from_zip(path)
    assert target.get_resource("chunk").path == ["data/chunk1.csv", "data/chunk2.csv"]
    assert target.get_resource("chunk").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_package_to_markdown_837():
    descriptor = {
        "name": "package",
        "resources": [
            {
                "name": "main",
                "schema": {
                    "fields": [
                        {
                            "name": "id",
                            "description": "Any positive integer",
                            "type": "integer",
                            "constraints": {"minimum": 1},
                        },
                        {
                            "name": "integer_minmax",
                            "description": "An integer between 1 and 10",
                            "type": "integer",
                            "constraints": {"minimum": 1, "maximum": 10},
                        },
                        {
                            "name": "boolean",
                            "description": "Any boolean",
                            "type": "boolean",
                        },
                    ],
                    "primaryKey": ["id"],
                },
            },
            {
                "name": "secondary",
                "schema": {
                    "fields": [
                        {
                            "name": "main_id",
                            "description": "Any value in main.id",
                            "type": "integer",
                        },
                        {
                            "name": "string",
                            "description": "Any string of up to 3 characters",
                            "type": "string",
                            "constraints": {"maxLength": 3},
                        },
                    ],
                    "foreignKeys": [
                        {
                            "fields": ["main_id"],
                            "reference": {"resource": "main", "fields": ["id"]},
                        }
                    ],
                },
            },
        ],
    }
    package = Package(descriptor)
    md_file_path = "data/fixtures/output-markdown/package.md"
    with open(md_file_path, encoding="utf-8") as file:
        expected = file.read()
    assert package.to_markdown().strip() == expected


def test_package_to_markdown_table_837():
    descriptor = {
        "name": "package",
        "resources": [
            {
                "name": "main",
                "schema": {
                    "fields": [
                        {
                            "name": "id",
                            "description": "Any positive integer",
                            "type": "integer",
                            "constraints": {"minimum": 1},
                        },
                        {
                            "name": "integer_minmax",
                            "description": "An integer between 1 and 10",
                            "type": "integer",
                            "constraints": {"minimum": 1, "maximum": 10},
                        },
                        {
                            "name": "boolean",
                            "description": "Any boolean",
                            "type": "boolean",
                        },
                    ],
                    "primaryKey": ["id"],
                },
            },
            {
                "name": "secondary",
                "schema": {
                    "fields": [
                        {
                            "name": "main_id",
                            "description": "Any value in main.id",
                            "type": "integer",
                        },
                        {
                            "name": "string",
                            "description": "Any string of up to 3 characters",
                            "type": "string",
                            "constraints": {"maxLength": 3},
                        },
                    ],
                    "foreignKeys": [
                        {
                            "fields": ["main_id"],
                            "reference": {"resource": "main", "fields": ["id"]},
                        }
                    ],
                },
            },
        ],
    }
    package = Package(descriptor)
    md_file_path = "data/fixtures/output-markdown/package-table.md"
    with open(md_file_path, encoding="utf-8") as file:
        expected = file.read()
    assert package.to_markdown(table=True).strip() == expected


def test_package_to_markdown_file_837(tmpdir):
    descriptor = descriptor = descriptor = {
        "name": "package",
        "resources": [
            {
                "name": "main",
                "schema": {
                    "fields": [
                        {
                            "name": "id",
                            "description": "Any positive integer",
                            "type": "integer",
                            "constraints": {"minimum": 1},
                        },
                        {
                            "name": "integer_minmax",
                            "description": "An integer between 1 and 10",
                            "type": "integer",
                            "constraints": {"minimum": 1, "maximum": 10},
                        },
                        {
                            "name": "boolean",
                            "description": "Any boolean",
                            "type": "boolean",
                        },
                    ],
                    "primaryKey": ["id"],
                },
            },
            {
                "name": "secondary",
                "schema": {
                    "fields": [
                        {
                            "name": "main_id",
                            "description": "Any value in main.id",
                            "type": "integer",
                        },
                        {
                            "name": "string",
                            "description": "Any string of up to 3 characters",
                            "type": "string",
                            "constraints": {"maxLength": 3},
                        },
                    ],
                    "foreignKeys": [
                        {
                            "fields": ["main_id"],
                            "reference": {"resource": "main", "fields": ["id"]},
                        }
                    ],
                },
            },
        ],
    }
    md_file_path = "data/fixtures/output-markdown/package.md"
    with open(md_file_path, encoding="utf-8") as file:
        expected = file.read()
    target = str(tmpdir.join("package.md"))
    package = Package(descriptor)
    package.to_markdown(path=target).strip()
    with open(target, encoding="utf-8") as file:
        output = file.read()
    assert expected == output
