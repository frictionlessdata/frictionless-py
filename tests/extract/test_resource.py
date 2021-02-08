import types
from pathlib import Path
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


def test_extract_resource_process_and_stream():
    process = lambda row: row.to_list()
    list_stream = extract("data/resource.json", process=process, stream=True)
    assert isinstance(list_stream, types.GeneratorType)
    assert list(list_stream) == [
        [1, "english"],
        [2, "中国人"],
    ]


def test_extract_resource_from_file():
    assert extract("data/table.csv") == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_resource_from_file_process():
    process = lambda row: row.to_list()
    assert extract("data/table.csv", process=process) == [
        [1, "english"],
        [2, "中国人"],
    ]


def test_extract_resource_from_file_stream():
    row_stream = extract("data/table.csv", stream=True)
    assert isinstance(row_stream, types.GeneratorType)
    assert list(row_stream) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_resource_from_file_pathlib():
    assert extract(Path("data/table.csv")) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_resource_from_file_process_and_stream():
    process = lambda row: row.to_list()
    list_stream = extract("data/table.csv", process=process, stream=True)
    assert isinstance(list_stream, types.GeneratorType)
    assert list(list_stream) == [
        [1, "english"],
        [2, "中国人"],
    ]
