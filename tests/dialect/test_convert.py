import json
from frictionless import Dialect


def test_dialect_from_descriptor_v1():
    dialect = Dialect.from_descriptor({"delimiter": ";"})
    assert dialect.to_descriptor() == {"csv": {"delimiter": ";"}}


# Yaml


def test_dialect_to_yaml():
    dialect = Dialect.from_descriptor("data/dialect.json")
    output_file_path = "data/fixtures/convert/dialect.yaml"
    with open(output_file_path) as file:
        assert dialect.to_yaml().strip() == file.read().strip()


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
