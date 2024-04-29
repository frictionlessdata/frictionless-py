from collections import OrderedDict

import pytest

from frictionless import Schema, formats
from frictionless.dialect.dialect import Dialect
from frictionless.resources import TableResource

# Read


def test_inline_parser():
    data = [["id", "name"], ["1", "english"], ["2", "中国人"]]
    with TableResource(data=data) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_inline_parser_keyed():
    data = [{"id": "1", "name": "english"}, {"id": "2", "name": "中国人"}]
    with TableResource(data=data, format="inline") as resource:
        assert resource.dialect.to_descriptor() == {"inline": {"keyed": True}}
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_inline_parser_keyed_order_is_preserved():
    data = [{"name": "english", "id": "1"}, {"name": "中国人", "id": "2"}]
    with TableResource(data=data, format="inline") as resource:
        assert resource.dialect.to_descriptor() == {"inline": {"keyed": True}}
        assert resource.header == ["name", "id"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_inline_parser_keyed_with_keys_provided():
    data = [{"id": "1", "name": "english"}, {"id": "2", "name": "中国人"}]
    control = formats.InlineControl(keys=["name", "id"])
    with TableResource(data=data, format="inline", control=control) as resource:
        assert resource.dialect.to_descriptor() == {
            "inline": {"keyed": True, "keys": ["name", "id"]}
        }
        assert resource.header == ["name", "id"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_inline_parser_from_generator():
    def data():
        yield ["id", "name"]
        yield ["1", "english"]
        yield ["2", "中国人"]

    with TableResource(data=data) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_inline_parser_from_generator_not_callable():
    def data():
        yield ["id", "name"]
        yield ["1", "english"]
        yield ["2", "中国人"]

    with TableResource(data=data()) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_inline_parser_from_ordered_dict():
    data = [
        OrderedDict([("name", "english"), ("id", "1")]),
        OrderedDict([("name", "中国人"), ("id", "2")]),
    ]
    with TableResource(data=data) as resource:
        rows = resource.read_rows()
        assert resource.dialect.to_descriptor() == {"inline": {"keyed": True}}
        assert resource.header == ["name", "id"]
        assert rows[0].cells == ["english", "1"]
        assert rows[1].cells == ["中国人", "2"]


def test_inline_parser_read_inline_data_with_missing_column_values():
    data = [{"id": 1}, {"id": 2, "name": "中国人"}]
    schema = {
        "fields": [{"name": "id", "type": "integer"}, {"name": "name", "type": "string"}]
    }
    with TableResource(data=data, schema=Schema.from_descriptor(schema)) as resource:
        assert resource.read_rows() == [
            {"id": 1, "name": None},
            {"id": 2, "name": "中国人"},
        ]


# Write


@pytest.mark.skip
def test_inline_parser_write(tmpdir):
    source = TableResource(path="data/table.csv")
    target = source.write(format="inline")
    assert target.data == [
        ["id", "name"],
        [1, "english"],
        [2, "中国人"],
    ]


@pytest.mark.skip
def test_inline_parser_write_keyed(tmpdir):
    control = formats.InlineControl(keyed=True)
    source = TableResource(path="data/table.csv")
    target = source.write(format="inline", control=control)
    assert target.data == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_inline_parser_write_skip_header():
    dialect = Dialect.from_descriptor({"header": False})
    target = TableResource(format="inline", dialect=dialect)
    with TableResource(path="data/table.csv") as resource:
        resource.write(target)
        assert target.data == [[1, "english"], [2, "中国人"]]
