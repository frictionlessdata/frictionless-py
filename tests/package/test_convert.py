import os
import json
import yaml
import pytest
from frictionless import Package, Resource, formats, platform


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


# Markdown


def test_package_to_markdown():
    package = Package(DESCRIPTOR)
    expected_file_path = "data/fixtures/output-markdown/package.md"

    # Reads
    with open(expected_file_path, encoding="utf-8") as file:
        print("\n", package.to_markdown().strip())
        assert package.to_markdown().strip() == file.read()


def test_package_to_markdown_file(tmpdir):
    package = Package(DESCRIPTOR)
    output_file_path = str(tmpdir.join("package.md"))
    expected_file_path = "data/fixtures/output-markdown/package.md"

    # Read - expected
    with open(expected_file_path, encoding="utf-8") as file:
        expected = file.read()

    # Write
    package.to_markdown(path=output_file_path).strip()

    # Read - output
    with open(output_file_path, encoding="utf-8") as file:
        assert expected == file.read()


def test_package_to_markdown_table():
    package = Package(DESCRIPTOR)
    expected_file_path = "data/fixtures/output-markdown/package-table.md"

    # Read
    with open(expected_file_path, encoding="utf-8") as file:
        assert package.to_markdown(table=True).strip() == file.read()


# ER Diagram


def test_package_to_erd():
    package = Package("data/package-storage.json")

    # Read
    with open("data/fixtures/dot-files/package.dot") as file:
        assert package.to_er_diagram().strip() == file.read().strip()


def test_package_to_erd_table_names_with_dash(tmpdir):
    # graphviz shows error if the table/field name has "-" so need to
    # wrap names with quotes ""
    package = Package("data/datapackage.json")
    expected_file_path = (
        "data/fixtures/dot-files/package-resource-names-including-dash.dot"
    )
    output_file_path = os.path.join(tmpdir, "output.dot")

    # Read - expected
    with open(expected_file_path) as file:
        expected = file.read()

    # Write
    package.to_er_diagram(output_file_path)

    # Read - output
    with open(output_file_path) as file:
        output = file.read()
    assert expected.strip() == output.strip()
    assert output.count('"number-two"')


def test_package_to_erd_without_table_relationships(tmpdir):
    package = Package("data/datapackage.json")
    expected_file_path = (
        "data/fixtures/dot-files/package-resource-names-including-dash.dot"
    )
    output_file_path = os.path.join(tmpdir, "output.dot")

    # Read - expected
    with open(expected_file_path) as file:
        expected = file.read()

    # Write
    package.to_er_diagram(output_file_path)

    # Read - soutput
    with open(output_file_path) as file:
        output = file.read()
    assert expected.strip() == output.strip()
    assert output.count("->") == 0
