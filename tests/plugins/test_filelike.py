import pytest
from frictionless import Resource


# Read


def test_filelike_loader():
    with open("data/table.csv", mode="rb") as file:
        with Resource(file, format="csv") as resource:
            assert resource.header == ["id", "name"]
            assert resource.read_rows() == [
                {"id": 1, "name": "english"},
                {"id": 2, "name": "中国人"},
            ]


def test_filelike_loader_without_open():
    with open("data/table.csv", mode="rb") as file:
        resource = Resource(path=file, format="csv")
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Write


@pytest.mark.skip
def test_filelike_loader_write():
    source = Resource("data/table.csv")
    target = Resource(scheme="filelike", format="csv")
    source.write(target)
    assert (
        target.read_bytes()
        == b"id,name\r\n1,english\r\n2,\xe4\xb8\xad\xe5\x9b\xbd\xe4\xba\xba\r\n"
    )
