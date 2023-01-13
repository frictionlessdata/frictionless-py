import os
import types
from pathlib import Path
from frictionless import Resource, system


# General


def test_extract_resource():
    resource = Resource("data/resource.json")
    assert resource.extract() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_resource_process():
    resource = Resource("data/resource.json")
    process = lambda row: row.to_list()
    assert resource.extract(process=process) == [
        [1, "english"],
        [2, "中国人"],
    ]


def test_extract_resource_stream():
    resource = Resource("data/resource.json")
    row_stream = resource.extract(stream=True)
    assert isinstance(row_stream, types.GeneratorType)
    assert list(row_stream) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_resource_process_and_stream():
    resource = Resource("data/resource.json")
    process = lambda row: row.to_list()
    cell_stream = resource.extract(process=process, stream=True)
    assert isinstance(cell_stream, types.GeneratorType)
    assert list(cell_stream) == [
        [1, "english"],
        [2, "中国人"],
    ]


def test_extract_resource_from_file():
    resource = Resource("data/table.csv")
    assert resource.extract() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_resource_from_file_process():
    resource = Resource("data/table.csv")
    process = lambda row: row.to_list()
    assert resource.extract(process=process) == [
        [1, "english"],
        [2, "中国人"],
    ]


def test_extract_resource_from_file_stream():
    resource = Resource("data/table.csv")
    row_stream = resource.extract(stream=True)
    assert isinstance(row_stream, types.GeneratorType)
    assert list(row_stream) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_resource_from_file_pathlib():
    resource = Resource(Path("data/table.csv"))
    assert resource.extract() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_resource_from_file_process_and_stream():
    resource = Resource("data/table.csv")
    process = lambda row: row.to_list()
    cell_stream = resource.extract(process=process, stream=True)
    assert isinstance(cell_stream, types.GeneratorType)
    assert list(cell_stream) == [
        [1, "english"],
        [2, "中国人"],
    ]


# Bugs


def test_extract_resource_from_json_format_issue_827():
    resource = Resource(path="data/table.json", type="table")
    rows = resource.extract()
    assert rows == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_resource_basepath_and_abspath_issue_856():
    descriptor = {"path": os.path.abspath("data/table.csv")}
    with system.use_context(trusted=True):
        resource = Resource(descriptor, basepath="data")
        assert resource.extract() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_extract_resource_string_with_leading_zeros_issue_1232_1364():
    resource = Resource("data/issue-1232.csv")
    rows = resource.extract(limit_rows=1)
    assert rows == [
        {
            "comune": 30151360,
            "codice_regione": 3,
            "codice_provincia": 15,
            "codice_comune": 1360,
            "denominazione_comune": "POLPENAZZE DEL GARDA",
            "sigla_provincia": "BS",
            "data_entrata_in_carica": "13/10/2021",
        }
    ]
