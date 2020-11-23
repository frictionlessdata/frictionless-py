from frictionless import Table, Resource


# Read


def test_table_stream():
    with open("data/table.csv", mode="rb") as file:
        with Table(file, format="csv") as table:
            assert table.header == ["id", "name"]
            assert table.read_data() == [["1", "english"], ["2", "中国人"]]


def test_resource_stream():
    with open("data/table.csv", mode="rb") as file:
        resource = Resource(path=file, format="csv")
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
