import pytest

from frictionless import platform
from frictionless.resources import TableResource

# Read


def test_buffer_loader():
    data = b"header1,header2\nvalue1,value2\nvalue3,value4"
    with TableResource(data=data, format="csv") as resource:
        assert resource.header == ["header1", "header2"]
        assert resource.read_rows() == [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]


# Write


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_buffer_loader_write():
    source = TableResource(path="data/table.csv")
    target = source.write(TableResource(scheme="buffer", format="csv"))
    assert target.data == "id,name\r\n1,english\r\n2,中国人\r\n".encode("utf-8")


# Bugs


def test_buffer_loader_recursion_error_issue_647():
    with open("data/issue-647.csv.txt", "rb") as file:
        with TableResource(
            data=file.read(), format="csv", encoding="iso-8859-1"
        ) as resource:
            assert len(resource.read_cells()) == 883
