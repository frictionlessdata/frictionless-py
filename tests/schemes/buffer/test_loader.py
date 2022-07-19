import pytest
from frictionless import Resource, platform


# Read


def test_buffer_loader():
    source = b"header1,header2\nvalue1,value2\nvalue3,value4"
    with Resource(source, format="csv") as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]


# Write


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_buffer_loader_write():
    source = Resource("data/table.csv")
    target = source.write(Resource(scheme="buffer", format="csv"))
    assert target.data == "id,name\r\n1,english\r\n2,中国人\r\n".encode("utf-8")


# Bugs


def test_buffer_loader_recursion_error_issue_647():
    with open("data/issue-647.csv.txt", "rb") as file:
        with Resource(file.read(), format="csv", encoding="iso-8859-1") as resource:
            assert len(resource.read_cells()) == 883
