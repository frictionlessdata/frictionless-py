import os
import json
import yaml
from frictionless import Package


DESCRIPTOR = {
    "name": "package",
    "resources": [
        {
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
    ],
}


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


def test_package_to_copy():
    source = Package.describe("data/chunk*.csv")
    target = source.to_copy()
    assert source is not target
    assert source.to_descriptor() == target.to_descriptor()


# Json/Yaml


def test_package_to_json(tmpdir):

    # Write
    target = os.path.join(tmpdir, "package.json")
    package = Package("data/package.json")
    package.to_json(target)

    # Read
    with open(target, encoding="utf-8") as file:
        assert package.to_descriptor() == json.load(file)


def test_package_to_yaml(tmpdir):

    # Write
    target = os.path.join(tmpdir, "package.yaml")
    package = Package("data/package.json")
    package.to_yaml(target)

    # Read
    with open(target, encoding="utf-8") as file:
        assert package.to_descriptor() == yaml.safe_load(file)
