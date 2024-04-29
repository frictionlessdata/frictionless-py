from frictionless.dialect.dialect import Dialect
from frictionless.resources import TableResource

# Read


def test_yaml_parser():
    with TableResource(path="data/table.yaml") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_yaml_parser_keyed():
    with TableResource(path="data/table.keyed.yaml") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Write


def test_yaml_parser_write(tmpdir):
    source = TableResource(path="data/table.csv")
    target = TableResource(path=str(tmpdir.join("table.yaml")))
    source.write(target)
    with target:
        assert target.format == "yaml"
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_yaml_parser_write_skip_header(tmpdir):
    dialect = Dialect.from_descriptor({"header": False})
    target = TableResource(path=str(tmpdir.join("table.yaml")), dialect=dialect)
    with TableResource(path="data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        resource.write_table(target)
        assert target.read_rows() == [
            {"field1": 1, "field2": "english"},
            {"field1": 2, "field2": "中国人"},
        ]
