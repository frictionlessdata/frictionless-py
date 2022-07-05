from frictionless import Resource
from importlib import import_module


# Read


def test_local_loader():
    with Resource("data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_local_loader_pathlib_path():
    pathlib = import_module("pathlib")
    with Resource(pathlib.Path("data/table.csv")) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
