import types
import pytest
from frictionless import extract, helpers


# General


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_extract_package():
    assert extract("data/package.json", dict=True) == {
        "data/table.csv": [{"id": 1, "name": "english"}, {"id": 2, "name": "中国人"}]
    }


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_extract_package_process():
    assert extract("data/package.json", list=True) == {
        "data/table.csv": [
            [1, "english"],
            [2, "中国人"],
        ],
    }


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_extract_package_stream():
    row_streams = extract("data/package.json", stream=True, dict=True)
    row_stream = row_streams["data/table.csv"]
    assert isinstance(row_stream, types.GeneratorType)
    assert list(row_stream) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_extract_package_process_and_stream():
    row_streams = extract("data/package.json", stream=True, list=True)
    row_stream = row_streams["data/table.csv"]
    assert isinstance(row_stream, types.GeneratorType)
    assert list(row_stream) == [
        [1, "english"],
        [2, "中国人"],
    ]
