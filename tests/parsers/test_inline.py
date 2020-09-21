from collections import OrderedDict
from frictionless import Table, dialects


# Read


def test_table_inline():
    source = [["id", "name"], ["1", "english"], ["2", "中国人"]]
    with Table(source) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


def test_table_inline_keyed():
    source = [{"id": "1", "name": "english"}, {"id": "2", "name": "中国人"}]
    with Table(source, format="inline") as table:
        assert table.dialect.keyed is True
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


def test_table_inline_keyed_with_keys_provided():
    source = [{"id": "1", "name": "english"}, {"id": "2", "name": "中国人"}]
    dialect = dialects.InlineDialect(keys=["name", "id"])
    with Table(source, format="inline", dialect=dialect) as table:
        assert table.dialect.keyed is True
        assert table.header == ["name", "id"]
        assert table.read_data() == [["english", "1"], ["中国人", "2"]]


def test_table_inline_from_iterator():
    source = iter([["id", "name"], ["1", "english"], ["2", "中国人"]])
    with Table(source) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


def test_table_inline_from_generator():
    def generator():
        yield ["id", "name"]
        yield ["1", "english"]
        yield ["2", "中国人"]

    with Table(generator) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


def test_table_inline_from_generator_not_callable():
    def generator():
        yield ["id", "name"]
        yield ["1", "english"]
        yield ["2", "中国人"]

    with Table(generator()) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


def test_table_inline_from_ordered_dict():
    source = [
        OrderedDict([("name", "english"), ("id", "1")]),
        OrderedDict([("name", "中国人"), ("id", "2")]),
    ]
    with Table(source) as table:
        assert table.dialect.keyed is True
        assert table.header == ["name", "id"]
        assert table.read_data() == [["english", "1"], ["中国人", "2"]]


# Write


def test_table_inline_write(tmpdir):
    source = "data/table.csv"
    target = []
    with Table(source) as table:
        table.write(target)
    assert target == [
        ["id", "name"],
        [1, "english"],
        [2, "中国人"],
    ]


def test_table_inline_write_keyed(tmpdir):
    source = "data/table.csv"
    target = []
    dialect = dialects.InlineDialect(keyed=True)
    with Table(source) as table:
        table.write(target, dialect=dialect)
    assert target == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
