import json

import pytest

from frictionless import formats
from frictionless.dialect.dialect import Dialect
from frictionless.resources import TableResource

BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Read


def test_json_parser():
    with TableResource(path="data/table.json") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_json_parser_keyed():
    with TableResource(path="data/table.keyed.json") as resource:
        assert resource.dialect.to_descriptor() == {"json": {"keyed": True}}
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_json_parser_keyed_with_keys_provided():
    control = formats.JsonControl(keys=["name", "id"])
    with TableResource(path="data/table.keyed.json", control=control) as resource:
        assert resource.dialect.to_descriptor() == {
            "json": {"keyed": True, "keys": ["name", "id"]}
        }
        assert resource.header == ["name", "id"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_json_parser_from_buffer():
    data = '[["id", "name"], [1, "english"], [2, "中国人"]]'.encode("utf-8")
    with TableResource(data=data, format="json") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_json_parser_from_buffer_keyed():
    data = '[{"id": 1, "name": "english" }, {"id": 2, "name": "中国人" }]'.encode("utf-8")
    with TableResource(data=data, format="json") as resource:
        assert resource.dialect.to_descriptor() == {"json": {"keyed": True}}
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_json_parser_from_remote():
    with TableResource(path=BASEURL % "data/table.json") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_json_parser_from_remote_keyed():
    with TableResource(path=BASEURL % "data/table.keyed.json") as resource:
        assert resource.dialect.to_descriptor() == {"json": {"keyed": True}}
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Write


def test_json_parser_write(tmpdir):
    source = TableResource(path="data/table.csv")
    target = TableResource(path=str(tmpdir.join("table.json")))
    target = source.write(target)
    assert target.normpath
    with open(target.normpath) as file:
        assert json.load(file) == [
            ["id", "name"],
            [1, "english"],
            [2, "中国人"],
        ]


def test_json_parser_write_decimal(tmpdir):
    control = formats.JsonControl(keyed=True)
    source = TableResource(data=[["id", "name"], [1.5, "english"], [2.5, "german"]])
    target = TableResource(path=str(tmpdir.join("table.json")), control=control)
    target = source.write(target)
    assert target.normpath
    with open(target.normpath) as file:
        assert json.load(file) == [
            {"id": "1.5", "name": "english"},
            {"id": "2.5", "name": "german"},
        ]


def test_json_parser_write_keyed(tmpdir):
    control = formats.JsonControl(keyed=True)
    source = TableResource(path="data/table.csv")
    target = TableResource(path=str(tmpdir.join("table.json")), control=control)
    target = source.write(target)
    assert target.normpath
    with open(target.normpath) as file:
        assert json.load(file) == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_json_parser_write_skip_header(tmpdir):
    dialect = Dialect.from_descriptor({"header": False})
    path = str(tmpdir.join("table.json"))
    target = TableResource(path=path, dialect=dialect)
    with TableResource(path="data/table.csv") as resource:
        target = resource.write(target)
        assert target.read_data() == [[1, "english"], [2, "中国人"]]
