from frictionless import formats
from frictionless.dialect.dialect import Dialect
from frictionless.resources import TableResource

# Read


def test_jsonl_parser():
    with TableResource(path="data/table.jsonl") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_jsonl_parser_ndjson():
    with TableResource(path="data/table.ndjson") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Write


def test_jsonl_parser_write(tmpdir):
    source = TableResource(path="data/table.csv")
    target = source.write(path=str(tmpdir.join("table.jsonl")))
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_jsonl_parser_write_keyed(tmpdir):
    control = formats.JsonControl(keyed=True)
    source = TableResource(path="data/table.csv")
    target = source.write(path=str(tmpdir.join("table.jsonl")), control=control)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_jsonl_parser_write_skip_header(tmpdir):
    dialect = Dialect.from_descriptor({"header": False})
    path = str(tmpdir.join("table.jsonl"))
    target = TableResource(path=path, dialect=dialect)
    with TableResource(path="data/table.csv") as resource:
        target = resource.write(target)
        assert target.read_rows() == [
            {"field1": 1, "field2": "english"},
            {"field1": 2, "field2": "中国人"},
        ]
