import io
from frictionless import Table


# Read


def test_table_stream():
    source = io.open("data/table.csv", mode="rb")
    with Table(source, format="csv") as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]
