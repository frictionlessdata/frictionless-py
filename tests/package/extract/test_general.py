import types
from frictionless import Package, helpers


IS_UNIX = not helpers.is_platform("windows")


# General


def test_extract_package():
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
    package = Package(path)
    assert package.extract() == {
        path: [{"id": 1, "name": "english"}, {"id": 2, "name": "中国人"}]
    }


def test_extract_package_process():
    process = lambda row: row.to_list()
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
    package = Package(path)
    assert package.extract(process=process) == {
        path: [
            [1, "english"],
            [2, "中国人"],
        ],
    }


def test_extract_package_stream():
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
    package = Package(path)
    row_streams = package.extract(stream=True)
    row_stream = row_streams[path]
    assert isinstance(row_stream, types.GeneratorType)
    assert list(row_stream) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_package_process_and_stream():
    process = lambda row: row.to_list()
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
    package = Package(path)
    list_streams = package.extract(process=process, stream=True)
    list_stream = list_streams[path]
    assert isinstance(list_stream, types.GeneratorType)
    assert list(list_stream) == [
        [1, "english"],
        [2, "中国人"],
    ]


def test_extract_package_descriptor_type_package():
    package = Package(descriptor="data/package/datapackage.json")
    data = package.extract()
    assert isinstance(data, dict)
