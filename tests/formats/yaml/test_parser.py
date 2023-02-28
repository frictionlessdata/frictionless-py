from frictionless import Resource, resources


# Read


def test_yaml_parser():
    with resources.TableResource(path="data/table.yaml") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_yaml_parser_keyed():
    with resources.TableResource(path="data/table.keyed.yaml") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Write


def test_yaml_parser_write(tmpdir):
    source = Resource("data/table.csv")
    target = resources.TableResource(path=str(tmpdir.join("table.yaml")))
    source.write(target)
    with target:
        assert target.format == "yaml"
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
