import types
import pytest
from frictionless import extract, helpers


# General


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_extract_package():
    assert extract("data/package.json") == {
        "data/table.csv": [{"id": 1, "name": "english"}, {"id": 2, "name": "中国人"}]
    }


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_extract_package_process():
    process = lambda row: row.to_list()
    assert extract("data/package.json", process=process) == {
        "data/table.csv": [
            [1, "english"],
            [2, "中国人"],
        ],
    }


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_extract_package_stream():
    row_streams = extract("data/package.json", stream=True)
    row_stream = row_streams["data/table.csv"]
    assert isinstance(row_stream, types.GeneratorType)
    assert list(row_stream) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_extract_package_process_and_stream():
    process = lambda row: row.to_list()
    list_streams = extract("data/package.json", process=process, stream=True)
    list_stream = list_streams["data/table.csv"]
    assert isinstance(list_stream, types.GeneratorType)
    assert list(list_stream) == [
        [1, "english"],
        [2, "中国人"],
    ]
