from frictionless import Resource


# Read


def test_yaml_parser():
    with Resource(path="data/table.yaml", type="table") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_yaml_parser_keyed():
    with Resource(path="data/table.keyed.yaml", type="table") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Write


def test_yaml_parser_write(tmpdir):
    source = Resource("data/table.csv")
    target = Resource(path=str(tmpdir.join("table.yaml")), type="table")
    source.write(target)
    with target:
        assert target.format == "yaml"
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
