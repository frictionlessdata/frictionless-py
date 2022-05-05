import sys
import pytest
from frictionless import Resource, helpers


IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Read


@pytest.mark.skipif(sys.version_info < (3, 7), reason="Requires Python3.7+")
def test_resource_read_bytes():
    resource = Resource(path="data/text.txt")
    bytes = resource.read_bytes()
    if IS_UNIX:
        assert bytes == b"text\n"


def test_resource_read_text():
    resource = Resource(path="data/text.txt")
    text = resource.read_text()
    if IS_UNIX:
        assert text == "text\n"


def test_resource_read_data():
    resource = Resource(path="data/table.json")
    assert resource.read_lists() == [
        ["id", "name"],
        [1, "english"],
        [2, "中国人"],
    ]


def test_resource_read_lists():
    resource = Resource(path="data/table.json")
    lists = resource.read_lists()
    assert lists == [
        ["id", "name"],
        [1, "english"],
        [2, "中国人"],
    ]


def test_resource_read_rows():
    resource = Resource(path="data/table.json")
    rows = resource.read_rows()
    assert rows == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
