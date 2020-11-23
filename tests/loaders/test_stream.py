import io
from frictionless import Table, Resource


# Read


def test_table_stream():
    source = io.open("data/table.csv", mode="rb")
    with Table(source, format="csv") as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


def test_resource_stream():
    source = io.open("data/table.csv", mode="rb")
    resource = Resource(path=source, format="csv")
    assert resource.read_header() == ["id", "name"]
    assert resource.read_data() == [["1", "english"], ["2", "中国人"]]
