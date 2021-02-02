import json
import pytest
from frictionless import Resource
from frictionless.plugins.json import JsonDialect

BASE_URL = "https://raw.githubusercontent.com/okfn/tabulator-py/master/%s"


# Read


def test_json_parser():
    with Resource(path="data/table.json") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_json_parser_keyed():
    with Resource(path="data/table.keyed.json") as resource:
        assert resource.dialect.keyed is True
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_json_parser_keyed_with_keys_provided():
    dialect = JsonDialect(keys=["name", "id"])
    with Resource(path="data/table.keyed.json", dialect=dialect) as resource:
        assert resource.dialect.keyed is True
        assert resource.header == ["name", "id"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_json_parser_from_text():
    source = '[["id", "name"], [1, "english"], [2, "中国人"]]'
    with Resource(source, scheme="text", format="json") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_json_parser_from_text_keyed():
    source = '[{"id": 1, "name": "english" }, {"id": 2, "name": "中国人" }]'
    with Resource(source, scheme="text", format="json") as resource:
        assert resource.dialect.keyed is True
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_json_parser_from_remote():
    with Resource(path=BASE_URL % "data/table-lists.json") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_json_parser_from_remote_keyed():
    with Resource(path=BASE_URL % "data/table-dicts.json") as resource:
        assert resource.dialect.keyed is True
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_jsonl_parser():
    with Resource("data/table.jsonl") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_jsonl_parser_ndjson():
    with Resource("data/table.ndjson") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Write


def test_json_parser_write(tmpdir):
    source = Resource("data/table.csv")
    target = Resource(path=str(tmpdir.join("table.json")))
    source.write(target)
    with open(target.fullpath) as file:
        assert json.load(file) == [
            ["id", "name"],
            [1, "english"],
            [2, "中国人"],
        ]


def test_json_parser_write_decimal(tmpdir):
    dialect = JsonDialect(keyed=True)
    source = Resource([["id", "name"], [1.5, "english"], [2.5, "german"]])
    target = Resource(path=str(tmpdir.join("table.json")), dialect=dialect)
    source.write(target)
    with open(target.fullpath) as file:
        assert json.load(file) == [
            {"id": "1.5", "name": "english"},
            {"id": "2.5", "name": "german"},
        ]


def test_json_parser_write_keyed(tmpdir):
    dialect = JsonDialect(keyed=True)
    source = Resource("data/table.csv")
    target = Resource(path=str(tmpdir.join("table.json")), dialect=dialect)
    source.write(target)
    with open(target.fullpath) as file:
        assert json.load(file) == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_jsonl_parser_write(tmpdir):
    source = Resource("data/table.csv")
    target = Resource(str(tmpdir.join("table.jsonl")))
    source.write(target)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_jsonl_parser_write_keyed(tmpdir):
    dialect = JsonDialect(keyed=True)
    source = Resource("data/table.csv")
    target = Resource(str(tmpdir.join("table.jsonl")), dialect=dialect)
    source.write(target)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
