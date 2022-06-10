import os
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


def test_extract_resource_from_json_format_issue_827():
    rows = extract(path="data/table.json")
    assert rows == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_resource_basepath_and_abspath_issue_856():
    descriptor = {"path": os.path.abspath("data/table.csv")}
    rows = extract(descriptor, basepath="data", trusted=True)
    assert rows == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_resource_valid_rows_1004():
    descriptor = {
        "name": "data1-resource",
        "path": "data/issue-1004/issue-1004-data1.csv",
    }
    output = extract(descriptor, valid=True)
    assert output == [
        {"id": 1, "neighbor_id": "Ireland", "name": "Britain", "population": "67"},
        {"id": 3, "neighbor_id": "22", "name": "Germany", "population": "83"},
        {"id": 4, "neighbor_id": None, "name": "Italy", "population": "60"},
    ]


def test_extract_resource_invalid_rows_1004():
    descriptor = {
        "name": "data1-resource",
        "path": "data/issue-1004/issue-1004-data1.csv",
    }
    output = extract(descriptor, valid=False)
    assert output == [
        {"id": 2, "neighbor_id": "3", "name": "France", "population": "n/a"},
        {"id": 5, "neighbor_id": None, "name": None, "population": None},
    ]


def test_extract_resource_with_resource_path_valid_rows_1004():
    assert extract("data/issue-1004/issue-1004-data1.csv", valid=True) == [
        {"id": 1, "neighbor_id": "Ireland", "name": "Britain", "population": "67"},
        {"id": 3, "neighbor_id": "22", "name": "Germany", "population": "83"},
        {"id": 4, "neighbor_id": None, "name": "Italy", "population": "60"},
    ]


def test_extract_resource_valid_rows_with_resource_file_path_1004():
    output = extract("data/issue-1004/issue-1004-resource.json", valid=True)
    assert output == [
        {"id": 1, "neighbor_id": "Ireland", "name": "Britain", "population": "67"},
        {"id": 3, "neighbor_id": "22", "name": "Germany", "population": "83"},
        {"id": 4, "neighbor_id": None, "name": "Italy", "population": "60"},
    ]


def test_extract_resource_process_valid_rows_1004():
    process = lambda row: row.to_list()
    descriptor = {
        "name": "data1-resource",
        "path": "data/issue-1004/issue-1004-data1.csv",
    }
    assert extract(descriptor, process=process, valid=True) == [
        [1, "Ireland", "Britain", "67"],
        [3, "22", "Germany", "83"],
        [4, None, "Italy", "60"],
    ]


def test_extract_resource_process_stream_valid_rows_1004():
    process = lambda row: row.to_list()
    descriptor = {
        "name": "data1-resource",
        "path": "data/issue-1004/issue-1004-data1.csv",
    }
    list_stream = extract(descriptor, process=process, stream=True, valid=True)
    assert isinstance(list_stream, types.GeneratorType)
    assert list(list_stream) == [
        [1, "Ireland", "Britain", "67"],
        [3, "22", "Germany", "83"],
        [4, None, "Italy", "60"],
    ]
