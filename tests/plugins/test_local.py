from frictionless import Table
from importlib import import_module


# Read


def test_table_file():
    with Table("data/table.csv") as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


def test_table_file_pathlib_path():
    pathlib = import_module("pathlib")
    with Table(pathlib.Path("data/table.csv")) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]
