import types
from frictionless import Package


# General


def test_extract_package():
    package = Package("data/table.csv")
    assert package.extract() == {
        "table": [{"id": 1, "name": "english"}, {"id": 2, "name": "中国人"}]
    }


def test_extract_package_process():
    process = lambda row: row.to_list()
    package = Package("data/table.csv")
    assert package.extract(process=process) == {
        "table": [
            [1, "english"],
            [2, "中国人"],
        ],
    }


def test_extract_package_stream():
    package = Package("data/table.csv")
    row_streams = package.extract(stream=True)
    row_stream = row_streams["table"]
    assert isinstance(row_stream, types.GeneratorType)
    assert list(row_stream) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_package_process_and_stream():
    process = lambda row: row.to_list()
    package = Package("data/table.csv")
    cell_streams = package.extract(process=process, stream=True)
    cell_stream = cell_streams["table"]
    assert isinstance(cell_stream, types.GeneratorType)
    assert list(cell_stream) == [
        [1, "english"],
        [2, "中国人"],
    ]


def test_extract_package_descriptor_type_package():
    package = Package("data/package/datapackage.json")
    data = package.extract()
    assert isinstance(data, dict)
