from frictionless import Resource
from frictionless.plugins.json import JsonDialect


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# General


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


def test_jsonl_parser_write(tmpdir):
    source = Resource("data/table.csv")
    target = source.write(str(tmpdir.join("table.jsonl")))
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_jsonl_parser_write_keyed(tmpdir):
    dialect = JsonDialect(keyed=True)
    source = Resource("data/table.csv")
    target = source.write(str(tmpdir.join("table.jsonl")), dialect=dialect)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
