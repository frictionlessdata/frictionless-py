import os
import json
import yaml
import pytest
from frictionless import Resource


DESCRIPTOR = {
    "name": "main",
    "path": "data/primary-file-types.csv",
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
}


# General


def test_resource_to_copy():
    source = Resource.describe("data/table.csv")
    target = source.to_copy()
    assert source.to_descriptor() == target.to_descriptor()


def test_resource_to_view():
    resource = Resource("data/table.csv")
    assert resource.to_view()


def test_resource_from_descriptor_layout_framework_v4():
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


# Bugs


def test_to_json_with_resource_data_is_not_a_list_issue_693():
    data = lambda: [["id", "name"], [1, "english"], [2, "german"]]
    resource = Resource(data=data)
    text = resource.to_json()
    assert json.loads(text) == {"data": []}


def test_to_yaml_with_resource_data_is_not_a_list_issue_693():
    data = lambda: [["id", "name"], [1, "english"], [2, "german"]]
    resource = Resource(data=data)
    text = resource.to_yaml()
    assert yaml.safe_load(text) == {"data": []}


def test_to_yaml_allow_unicode_issue_844():
    resource = Resource("data/issue-844.csv", encoding="utf-8")
    resource.infer()
    text = resource.to_yaml()
    assert "età" in text
