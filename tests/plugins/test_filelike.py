from frictionless import Table, Resource


# Read


def test_filelike_loader():
    with open("data/table.csv", mode="rb") as file:
        with Table(file, format="csv") as table:
            assert table.header == ["id", "name"]
            assert table.read_data() == [["1", "english"], ["2", "中国人"]]


def test_filelike_loader_resource():
    with open("data/table.csv", mode="rb") as file:
        resource = Resource(path=file, format="csv")
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Write


def test_filelike_loader_write():
    source = "data/table.csv"
    with Table(source) as table:
        byte_stream = table.write(scheme="filelike", format="csv")
    assert (
        byte_stream.read()
        == b"id,name\r\n1,english\r\n2,\xe4\xb8\xad\xe5\x9b\xbd\xe4\xba\xba\r\n"
    )
