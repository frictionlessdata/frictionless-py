import types
from frictionless import extract


# General


def test_extract_resource():
    assert extract("data/resource.json") == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_resource_process():
    process = lambda row: row.to_list()
    assert extract("data/resource.json", process=process) == [
        [1, "english"],
        [2, "中国人"],
    ]


def test_extract_resource_stream():
    row_stream = extract("data/resource.json", stream=True)
    assert isinstance(row_stream, types.GeneratorType)
    assert list(row_stream) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_table_process_and_stream():
    process = lambda row: row.to_list()
    data_stream = extract("data/resource.json", process=process, stream=True)
    assert isinstance(data_stream, types.GeneratorType)
    assert list(data_stream) == [
        [1, "english"],
        [2, "中国人"],
    ]
