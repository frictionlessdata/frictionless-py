import json
import pytest
from frictionless import Table, dialects

BASE_URL = "https://raw.githubusercontent.com/okfn/tabulator-py/master/%s"


# Read


def test_table_json():
    with Table("data/table.json") as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


def test_table_json_keyed():
    with Table("data/table.keyed.json") as table:
        assert table.dialect.keyed is True
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


def test_table_json_keyed_with_keys_provided():
    dialect = dialects.JsonDialect(keys=["name", "id"])
    with Table("data/table.keyed.json", dialect=dialect) as table:
        assert table.dialect.keyed is True
        assert table.header == ["name", "id"]
        assert table.read_data() == [["english", 1], ["中国人", 2]]


def test_table_json_from_text():
    source = '[["id", "name"], [1, "english"], [2, "中国人"]]'
    with Table(source, scheme="text", format="json") as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


def test_table_json_from_text_keyed():
    source = '[{"id": 1, "name": "english" }, {"id": 2, "name": "中国人" }]'
    with Table(source, scheme="text", format="json") as table:
        assert table.dialect.keyed is True
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


@pytest.mark.ci
def test_table_json_from_remote():
    with Table(BASE_URL % "data/table-lists.json") as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


@pytest.mark.ci
def test_table_json_from_remote_keyed():
    with Table(BASE_URL % "data/table-dicts.json") as table:
        assert table.dialect.keyed is True
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


def test_table_jsonl():
    with Table("data/table.jsonl") as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


def test_table_ndjson():
    with Table("data/table.ndjson") as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


# Write


def test_table_json_write(tmpdir):
    source = "data/table.csv"
    target = str(tmpdir.join("table.json"))
    with Table(source) as table:
        table.write(target)
    with open(target) as file:
        assert json.load(file) == [
            ["id", "name"],
            [1, "english"],
            [2, "中国人"],
        ]


def test_table_json_write_keyed(tmpdir):
    source = "data/table.csv"
    target = str(tmpdir.join("table.json"))
    dialect = dialects.JsonDialect(keyed=True)
    with Table(source) as table:
        table.write(target, dialect=dialect)
    with open(target) as file:
        assert json.load(file) == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_table_jsonl_write(tmpdir):
    source = "data/table.csv"
    target = str(tmpdir.join("table.jsonl"))
    with Table(source) as table:
        table.write(target)
    with Table(target) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]


def test_table_jsonl_write_keyed(tmpdir):
    source = "data/table.csv"
    target = str(tmpdir.join("table.jsonl"))
    dialect = dialects.JsonDialect(keyed=True)
    with Table(source) as table:
        table.write(target, dialect=dialect)
    with Table(target, dialect=dialect) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [[1, "english"], [2, "中国人"]]
