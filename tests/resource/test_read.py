import sys
import pytest
from frictionless import Resource, platform


# General


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
@pytest.mark.skipif(sys.version_info < (3, 7), reason="Requires Python3.7+")
def test_resource_read_bytes():
    resource = Resource(path="data/text.txt")
    bytes = resource.read_bytes()
    assert bytes == b"text\n"


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_read_bytes_bug_1341():
    assert len(Resource("data/issue-1341.csv").read_bytes()) == 16792
    assert len(Resource("data/issue-1066.csv").read_bytes()) == 3289808


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_read_text():
    resource = Resource(path="data/text.txt")
    text = resource.read_text()
    assert text == "text\n"


def test_resource_read_data():
    resource = Resource(path="data/table.json", type="table")
    assert resource.read_cells() == [
        ["id", "name"],
        [1, "english"],
        [2, "中国人"],
    ]


def test_resource_read_cells():
    resource = Resource(path="data/table.json", type="table")
    assert resource.read_cells() == [
        ["id", "name"],
        [1, "english"],
        [2, "中国人"],
    ]


def test_resource_read_rows():
    resource = Resource(path="data/table.json", type="table")
    rows = resource.read_rows()
    assert rows == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
