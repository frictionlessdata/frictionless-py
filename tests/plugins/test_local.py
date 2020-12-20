from frictionless import Table
from importlib import import_module


# Read


def test_local_loader():
    with Table("data/table.csv") as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_local_loader_pathlib_path():
    pathlib = import_module("pathlib")
    with Table(pathlib.Path("data/table.csv")) as table:
        assert table.header == ["id", "name"]
        assert table.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
