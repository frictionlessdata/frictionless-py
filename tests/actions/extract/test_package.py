import types
from frictionless import extract


# General


def test_extract_package():
    assert extract("data/package.json") == {
        "name": [{"id": 1, "name": "english"}, {"id": 2, "name": "中国人"}]
    }


def test_extract_package_process():
    process = lambda row: row.to_list()
    assert extract("data/package.json", process=process) == {
        "name": [
            [1, "english"],
            [2, "中国人"],
        ],
    }


def test_extract_package_stream():
    row_streams = extract("data/package.json", stream=True)
    row_stream = row_streams["name"]  # type: ignore
    assert isinstance(row_stream, types.GeneratorType)
    assert list(row_stream) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_package_process_and_stream():
    process = lambda row: row.to_list()
    cell_streams = extract("data/package.json", process=process, stream=True)
    cell_stream = cell_streams["name"]  # type: ignore
    assert isinstance(cell_stream, types.GeneratorType)
    assert list(cell_stream) == [
        [1, "english"],
        [2, "中国人"],
    ]


def test_extract_package_descriptor_type_package():
    data = extract("data/package/datapackage.json")
    assert isinstance(data, dict)
