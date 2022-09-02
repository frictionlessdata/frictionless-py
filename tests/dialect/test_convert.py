import json
import yaml
from frictionless import Dialect


def test_dialect_from_descriptor_standards_v1():
    dialect = Dialect.from_descriptor({"delimiter": ";"})
    assert dialect.to_descriptor() == {"csv": {"delimiter": ";"}}


# Yaml


def test_dialect_to_yaml():
    dialect = Dialect.from_descriptor("data/dialect.json")
    expected_file_path = "data/dialect.yaml"

    # Read
    with open(expected_file_path) as file:
        assert yaml.safe_load(dialect.to_yaml()) == yaml.safe_load(file.read())


# Json


def test_dialect_to_json():
    dialect = Dialect.from_descriptor("data/dialect.yaml")
    assert json.loads(dialect.to_json()) == {"csv": {"delimiter": ";"}}


# Markdown


def test_dialect_to_markdown():
    dialect = Dialect.from_descriptor("data/dialect.json")
    output_file_path = "data/fixtures/convert/dialect.md"
    with open(output_file_path) as file:
        assert dialect.to_markdown().strip() == file.read()
