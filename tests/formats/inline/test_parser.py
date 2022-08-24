from collections import OrderedDict
from frictionless import Resource, formats


# Read


def test_inline_parser():
    source = [["id", "name"], ["1", "english"], ["2", "中国人"]]
    with Resource(source) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_inline_parser_keyed():
    source = [{"id": "1", "name": "english"}, {"id": "2", "name": "中国人"}]
    with Resource(source, format="inline") as resource:
        assert resource.dialect.to_descriptor() == {"inline": {"keyed": True}}
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_inline_parser_keyed_order_is_preserved():
    source = [{"name": "english", "id": "1"}, {"name": "中国人", "id": "2"}]
    with Resource(source, format="inline") as resource:
        assert resource.dialect.to_descriptor() == {"inline": {"keyed": True}}
        assert resource.header == ["name", "id"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_inline_parser_keyed_with_keys_provided():
    source = [{"id": "1", "name": "english"}, {"id": "2", "name": "中国人"}]
    control = formats.InlineControl(keys=["name", "id"])
    with Resource(source, format="inline", control=control) as resource:
        assert resource.dialect.to_descriptor() == {
            "inline": {"keyed": True, "keys": ["name", "id"]}
        }
        assert resource.header == ["name", "id"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_inline_parser_from_generator():
    def generator():
        yield ["id", "name"]
        yield ["1", "english"]
        yield ["2", "中国人"]

    with Resource(generator) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_inline_parser_from_generator_not_callable():
    def generator():
        yield ["id", "name"]
        yield ["1", "english"]
        yield ["2", "中国人"]

    with Resource(generator()) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_inline_parser_from_ordered_dict():
    source = [
        OrderedDict([("name", "english"), ("id", "1")]),
        OrderedDict([("name", "中国人"), ("id", "2")]),
    ]
    with Resource(source) as resource:
        rows = resource.read_rows()
        assert resource.dialect.to_descriptor() == {"inline": {"keyed": True}}
        assert resource.header == ["name", "id"]
        assert rows[0].cells == ["english", "1"]
        assert rows[1].cells == ["中国人", "2"]


# Write


def test_inline_parser_write(tmpdir):
    source = Resource("data/table.csv")
    target = source.write(format="inline")
    assert target.data == [
        ["id", "name"],
        [1, "english"],
        [2, "中国人"],
    ]


def test_inline_parser_write_keyed(tmpdir):
    control = formats.InlineControl(keyed=True)
    source = Resource("data/table.csv")
    target = source.write(format="inline", control=control)
    assert target.data == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
