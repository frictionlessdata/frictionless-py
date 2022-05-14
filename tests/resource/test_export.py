import os
import json
import yaml
from frictionless import Resource, describe_resource, helpers


IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Export/Import


def test_resource_to_copy():
    source = describe_resource("data/table.csv")
    target = source.to_copy()
    assert source == target


def test_resource_to_json(tmpdir):
    target = os.path.join(tmpdir, "resource.json")
    resource = Resource("data/resource.json")
    resource.to_json(target)
    with open(target, encoding="utf-8") as file:
        assert resource == json.load(file)


def test_resource_to_yaml(tmpdir):
    target = os.path.join(tmpdir, "resource.yaml")
    resource = Resource("data/resource.json")
    resource.to_yaml(target)
    with open(target, encoding="utf-8") as file:
        assert resource == yaml.safe_load(file)


def test_to_json_with_resource_data_is_not_a_list_issue_693():
    data = lambda: [["id", "name"], [1, "english"], [2, "german"]]
    resource = Resource(data=data)
    text = resource.to_json()
    assert text == "{}"


def test_to_yaml_with_resource_data_is_not_a_list_issue_693():
    data = lambda: [["id", "name"], [1, "english"], [2, "german"]]
    resource = Resource(data=data)
    text = resource.to_yaml()
    assert text == "{}\n"


def test_to_yaml_allow_unicode_issue_844():
    resource = Resource("data/issue-844.csv", encoding="utf-8")
    resource.infer()
    text = resource.to_yaml()
    assert "età" in text


def test_resource_to_view():
    resource = Resource("data/table.csv")
    assert resource.to_view()


def test_resource_to_markdown_path_schema_837():
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


def test_resource_to_markdown_path_schema_table_837():
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


def test_resource_to_markdown_file_837(tmpdir):
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
