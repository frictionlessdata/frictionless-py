import json
import pytest
from frictionless import Resource, Dialect
from frictionless.plugins.json import JsonControl


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


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
        assert resource.dialect.get_control("json").keyed is True
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_json_parser_keyed_with_keys_provided():
    dialect = Dialect(controls=[JsonControl(keys=["name", "id"])])
    with Resource(path="data/table.keyed.json", dialect=dialect) as resource:
        assert resource.dialect.get_control("json").keyed is True
        assert resource.header == ["name", "id"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_json_parser_from_buffer():
    source = '[["id", "name"], [1, "english"], [2, "中国人"]]'.encode("utf-8")
    with Resource(source, format="json") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_json_parser_from_buffer_keyed():
    source = '[{"id": 1, "name": "english" }, {"id": 2, "name": "中国人" }]'.encode("utf-8")
    with Resource(source, format="json") as resource:
        assert resource.dialect.get_control("json").keyed is True
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_json_parser_from_remote():
    with Resource(path=BASEURL % "data/table.json") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_json_parser_from_remote_keyed():
    with Resource(path=BASEURL % "data/table.keyed.json") as resource:
        assert resource.dialect.get_control("json").keyed is True
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Write


def test_json_parser_write(tmpdir):
    source = Resource("data/table.csv")
    target = source.write(Resource(path=str(tmpdir.join("table.json"))))
    with open(target.fullpath) as file:
        assert json.load(file) == [
            ["id", "name"],
            [1, "english"],
            [2, "中国人"],
        ]


@pytest.mark.skip
def test_json_parser_write_decimal(tmpdir):
    dialect = Dialect(controls=[JsonControl(keyed=True)])
    source = Resource([["id", "name"], [1.5, "english"], [2.5, "german"]])
    target = source.write(Resource(path=str(tmpdir.join("table.json")), dialect=dialect))
    with open(target.fullpath) as file:
        assert json.load(file) == [
            {"id": "1.5", "name": "english"},
            {"id": "2.5", "name": "german"},
        ]


@pytest.mark.skip
def test_json_parser_write_keyed(tmpdir):
    dialect = Dialect(controls=[JsonControl(keyed=True)])
    source = Resource("data/table.csv")
    target = source.write(Resource(path=str(tmpdir.join("table.json")), dialect=dialect))
    with open(target.fullpath) as file:
        assert json.load(file) == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
