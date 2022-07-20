import os
import json
import yaml
import pytest
from frictionless import Resource


# General


def test_resource_to_copy():
    source = Resource.describe("data/table.csv")
    target = source.to_copy()
    assert source.to_descriptor() == target.to_descriptor()


def test_resource_to_view():
    resource = Resource("data/table.csv")
    assert resource.to_view()


def test_resource_from_descriptor_layout_v1x5():
    with pytest.warns(UserWarning):
        resource = Resource.from_descriptor(
            {
                "path": "data/table.csv",
                "layout": {"header": False},
            }
        )
        assert resource.to_descriptor() == {
            "path": "data/table.csv",
            "dialect": {"header": False},
        }


# Json/Yaml


def test_resource_to_json(tmpdir):
    target = os.path.join(tmpdir, "resource.json")
    resource = Resource("data/resource.json")
    resource.to_json(target)
    with open(target, encoding="utf-8") as file:
        assert json.load(file) == {
            "name": "name",
            "path": "table.csv",
        }


def test_resource_to_yaml(tmpdir):
    target = os.path.join(tmpdir, "resource.yaml")
    resource = Resource("data/resource.json")
    resource.to_yaml(target)
    with open(target, encoding="utf-8") as file:
        assert yaml.safe_load(file) == {
            "name": "name",
            "path": "table.csv",
        }


# Markdown


def test_resource_to_markdown_path_schema():
    descriptor = {
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
            ],
            "primaryKey": ["id"],
        },
    }
    resource = Resource(descriptor)
    md_file_path = "data/fixtures/output-markdown/resource.md"
    with open(md_file_path, encoding="utf-8") as file:
        expected = file.read()
    assert resource.to_markdown().strip() == expected


@pytest.mark.xfail
def test_resource_to_markdown_path_schema_table():
    descriptor = {
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
            ],
            "primaryKey": ["id"],
        },
    }
    resource = Resource(descriptor)
    md_file_path = "data/fixtures/output-markdown/resource-table.md"
    with open(md_file_path, encoding="utf-8") as file:
        expected = file.read()
    assert resource.to_markdown(table=True).strip() == expected


def test_resource_to_markdown_file(tmpdir):
    descriptor = descriptor = {
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
            ],
            "primaryKey": ["id"],
        },
    }
    md_file_path = "data/fixtures/output-markdown/resource.md"
    with open(md_file_path, encoding="utf-8") as file:
        expected = file.read()
    target = str(tmpdir.join("resource.md"))
    resource = Resource(descriptor)
    resource.to_markdown(path=target).strip()
    with open(target, encoding="utf-8") as file:
        output = file.read()
    assert expected == output


# Bugs


@pytest.mark.xfail(reason="Recover")
def test_to_json_with_resource_data_is_not_a_list_issue_693():
    data = lambda: [["id", "name"], [1, "english"], [2, "german"]]
    resource = Resource(data=data)
    text = resource.to_json()
    assert json.loads(text) == {}


@pytest.mark.xfail(reason="Recover")
def test_to_yaml_with_resource_data_is_not_a_list_issue_693():
    data = lambda: [["id", "name"], [1, "english"], [2, "german"]]
    resource = Resource(data=data)
    text = resource.to_yaml()
    assert yaml.safe_load(text) == {}


def test_to_yaml_allow_unicode_issue_844():
    resource = Resource("data/issue-844.csv", encoding="utf-8")
    resource.infer()
    text = resource.to_yaml()
    assert "età" in text


@pytest.mark.xfail(reason="Fix metadata_descriptor_path / normalization problem")
def test_resource_to_descriptor_infer_dereferencing_issue_904():
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
