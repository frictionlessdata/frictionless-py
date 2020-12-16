import types
from frictionless import extract


# General


def test_extract_resource():
    assert extract("data/resource.json", dict=True) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_resource_process():
    assert extract("data/resource.json", list=True) == [
        [1, "english"],
        [2, "中国人"],
    ]


def test_extract_resource_stream():
    row_stream = extract("data/resource.json", stream=True, dict=True)
    assert isinstance(row_stream, types.GeneratorType)
    assert list(row_stream) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_table_process_and_stream():
    row_stream = extract("data/resource.json", stream=True, list=True)
    assert isinstance(row_stream, types.GeneratorType)
    assert list(row_stream) == [
        [1, "english"],
        [2, "中国人"],
    ]
